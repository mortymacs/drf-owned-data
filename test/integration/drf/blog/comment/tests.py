from rest_framework.test import APITestCase


class PostTest(APITestCase):
    pass

# Defined:
# 2 posts from User A and User B.

# Senaior:
# 1. User A:
# 1.1 Login.
# 1.2 Empty list of comments in his admin panel.
# 1.3 Put a comment on User B's post.
# 1.4 One item in his comments list in the admin panel.
# 1.5 Logout.

# 2. User B:
# 2.1 Login.
# 2.2 Empty list of posts in his admin panel.
# 2.3 Should be able to see the User A post.
# 2.4 Permission denied edit or delete the post.
# 1.3 Create a new post.
# 2.5 Logout.

# 3. User C [group:editor]:
# 3.1 Login.
# 3.2 Empty list of posts in his admin panel.
# 3.3 Should be able to see the posts of User A and B.
# 3.4 Should be able to only edit the post.
# 3.5 Permission denied delete the post.
# 3.5 Logout.

# 4. Anonymous
# 4.1 Permission denied on getting access to see his posts.
# 4.2 Should be able to see the posts of User A and B.
# 4.3 Permission denied on any other actions on posts.

# 4. User D [superuser]
# 4.1 Login
# 4.2 List of both User A and B posts in the admin panel.
# 4.3 Should be able to edit both posts.
# 4.4 Should be able to delete both posts.
# 4.5 Logout.

