def avatar_upload_to(instance, filename):

    return f"avatars/user_{instance.pk or 'new'}/{filename}"
