from django.urls import path


from . import views


app_name = "users"


urlpatterns = [

    path("list/", views.participants, name="participants"),

    path("register/", views.register_view, name="register"),

    path("login/", views.login_view, name="login"),

    path("logout/", views.logout_view, name="logout"),

    path("change-password/", views.change_password, name="change_password"),

    path("edit-profile/", views.edit_profile, name="edit_profile"),

    path("skills/", views.skill_suggest, name="skill_suggest"),

    path("<int:user_id>/", views.profile, name="profile"),

    path("<int:user_id>/skills/add/", views.add_skill, name="add_skill"),

    path("<int:user_id>/skills/<int:skill_id>/remove/", views.remove_skill, name="remove_skill"),

]
