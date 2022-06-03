from django.test import TestCase

# Senaior:
# 1. User A:
# 1.1 Login.
# 1.2 Empty list of jobs in his admin panel.
# 1.3 Create a new job.
# 1.4 One item in the list of jobs in his admin panel.
# 1.5 Logout.

# 2. User B:
# 2.1 Login.
# 2.2 List of jobs should contain User A's job in the admin panel.
# 2.3 Should be able to see the User A job in detail.
# 2.4 Permission denied edit or delete the post.
# 1.3 Create a new job.
# 2.5 Logout.

# 3. User C [group:bot]:
# 3.1 Login.
# 3.2 List of jobs should contain both users jobs in the admin panel.
# 3.3 Should be able to see the jobs of User A and B in detail.
# 3.4 Should be able to only cancel those jobs.
# 3.4 Should be able to only resume those jobs.
# 3.5 Permission denied create a new job.
# 3.5 Logout.

# 4. Anonymous
# 4.1 Permission denied on getting access to see his posts.
# 4.2 Permission denied on any actions even GET.

# 4. User D [superuser]
# 4.1 Login
# 4.2 List of jobs should contain both users jobs in the admin panel.
# 4.3 Should be able to resume both jobs.
# 4.3 Should be able to cancel both jobs.
# 4.4 Should be able to delete both jobs.
# 4.5 Logout.

