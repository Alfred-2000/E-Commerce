
from django.urls import path
from accounts.views import (
    LoginView,
    RegisterUser,
    ListDeleteUsers,
    RetrieveUpdateDeleteUser,
)

urlpatterns = [
    path('list/', ListDeleteUsers.as_view()),  #List accounts
    path('register/', RegisterUser.as_view(), name='account-register'),  #Register accounts
    path('<uuid:user_id>/', RetrieveUpdateDeleteUser.as_view()),    #Retrieve, Update, Delete account
]