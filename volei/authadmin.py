from db import supabase

def is_admin(user_id):
    res = supabase.table("roles") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("role", "admin") \
        .execute()

    return len(res.data) > 0