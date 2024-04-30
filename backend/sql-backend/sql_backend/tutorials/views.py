from django.shortcuts import render
from django.db import transaction, connection

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from tutorials.models import Tutorial
from tutorials.serializers import TutorialSerializer, UserSerializer
from rest_framework.decorators import api_view

from django.contrib.auth.models import User


from django.db import connection

@api_view(['GET', 'POST', 'DELETE'])
def tutorial_list(request):
    if request.method == 'GET':
        title = request.GET.get('title', None)
        is_published = request.GET.get('isPublished', None)

        with connection.cursor() as cursor:
            if title:
                title_filter = f"title ILIKE '%%{title}%%'"
            else:
                title_filter = "TRUE"  # Always true if no title filter

            if is_published:
                is_published = is_published.lower() == 'true'
                published_filter = f"AND published = {is_published}"
            else:
                published_filter = ""

            # Execute query to fetch tutorials
            cursor.execute(f"""
                SELECT * FROM tutorials_tutorial WHERE {title_filter} {published_filter};
            """)
            tutorials_rows = cursor.fetchall()

        # Convert fetched rows to Tutorial instances using ORM to access related users
        tutorials = [Tutorial.objects.get(pk=row[0]) for row in tutorials_rows]
        total = len(tutorials)
        published = sum(1 for tutorial in tutorials if tutorial.published)

        # Calculate total users and average users per tutorial
        total_users = sum(tutorial.users.count() for tutorial in tutorials)
        avg_users = total_users / total if total > 0 else 0

        # Serialize the tutorials
        tutorials_serializer = TutorialSerializer(tutorials, many=True)
        report = {
            'total': total,
            'published': published,
            'total_students': total_users,  # Renaming as 'total_users' for clarity
            'average_students': avg_users   # Renaming as 'average_users_per_tutorial' might be more descriptive
        }

        return JsonResponse({
            'tutorials': tutorials_serializer.data,
            'report': report
        }, safe=False)

    elif request.method == 'POST':
        print("Creating a new tutorial...\n")
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = TutorialSerializer(data=tutorial_data)
        if tutorial_serializer.is_valid():
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Assuming the fields in Tutorial model are 'title' and 'description'
                    cursor.execute("""
                        PREPARE insert_tutorial (varchar, varchar, boolean) AS
                        INSERT INTO tutorials_tutorial (title, description, published) VALUES ($1, $2, $3) RETURNING id;
                    """)
                    cursor.execute("EXECUTE insert_tutorial (%s, %s, %s)", [
                        tutorial_data['title'], 
                        tutorial_data['description'], 
                        tutorial_data.get('published', False)
                    ])
                    new_tutorial_id = cursor.fetchone()[0]
                    tutorial_data['id'] = new_tutorial_id
                
                # Adding users using ORM (to keep it simple)
                if 'users' in tutorial_data:
                    tutorial = Tutorial.objects.get(id=tutorial_data['id'])
                    for user_id in tutorial_data['users']:
                        tutorial.users.add(user_id)
                    
            return JsonResponse(tutorial_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    PREPARE delete_all_tutorials AS
                    DELETE FROM tutorials_tutorial;
                """)
                cursor.execute("EXECUTE delete_all_tutorials")
                cursor.execute("SELECT COUNT(*) FROM tutorials_tutorial;")
                count = cursor.fetchone()[0]
        
        return JsonResponse({'message': '{} Tutorials were deleted successfully!'.format(count)}, status=status.HTTP_204_NO_CONTENT)

 
 
@api_view(['GET', 'PUT', 'DELETE'])
def tutorial_detail(request, pk):
    try: 
        tutorial = Tutorial.objects.get(pk=pk) 
    except Tutorial.DoesNotExist: 
        return JsonResponse({'message': 'The tutorial does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    if request.method == 'GET': 
        tutorial_serializer = TutorialSerializer(tutorial) 
        return JsonResponse(tutorial_serializer.data) 
 
    elif request.method == 'PUT': 
        tutorial_data = JSONParser().parse(request) 
        tutorial_serializer = TutorialSerializer(tutorial, data=tutorial_data) 
        if tutorial_serializer.is_valid(): 
            tutorial_serializer.save()
            if 'users' in tutorial_data:
                users = tutorial_data['users']
                tutorial = Tutorial.objects.get(id=tutorial_serializer.data['id'])
                tutorial.users.clear()
                for user in users:
                    tutorial.users.add(user)
            return JsonResponse(tutorial_serializer.data) 
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
 
    elif request.method == 'DELETE': 
        with transaction.atomic():
            tutorial.delete() 
        return JsonResponse({'message': 'Tutorial was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    
        
@api_view(['GET'])
def tutorial_list_published(request):
    tutorials = Tutorial.objects.filter(published=True)

    if request.method == 'GET': 
        tutorials_serializer = TutorialSerializer(tutorials, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)
        # 'safe=False' for objects serialization

@api_view(['GET'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        users_serializer = UserSerializer(users, many=True)
        return JsonResponse(users_serializer.data, safe=False)

@api_view(['POST'])
def tutorial_users_manage(request, tutorial_pk):
    try:
        tutorial = Tutorial.objects.get(pk=tutorial_pk)
    except Tutorial.DoesNotExist:
        return JsonResponse({'message': 'The tutorial does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        with transaction.atomic():
            users_data = JSONParser().parse(request)
            for user_id in users_data.get('users', []):
                try:
                    user = User.objects.get(pk=user_id)
                    tutorial.users.add(user)
                except User.DoesNotExist:
                    continue 
        return JsonResponse({'message': 'Users were added successfully to the tutorial.'}, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
def user_detail(request, pk):
    """
    Retrieve an individual user's details by ID.
    """
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return JsonResponse({'message': 'The user does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data)
