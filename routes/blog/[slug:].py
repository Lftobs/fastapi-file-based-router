blog_posts = {
    "hello-world": {
        "title": "Hello World",
        "content": "This is my first blog post!",
        "author": "Alice",
        "tags": ["introduction", "hello"],
    },
    "python-tips": {
        "title": "10 Python Tips",
        "content": "Here are 10 useful Python tips for beginners...",
        "author": "Bob",
        "tags": ["python", "programming", "tips"],
    },
    "fastapi-guide": {
        "title": "FastAPI Getting Started",
        "content": "Learn how to build APIs with FastAPI...",
        "author": "Charlie",
        "tags": ["fastapi", "api", "python"],
    },
}


def get(slug: str):
    """Get blog post by slug."""
    from fastapi import HTTPException

    post = blog_posts.get(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    return {"slug": slug, "post": post}


def put(slug: str):
    """Update blog post by slug."""
    if slug not in blog_posts:
        # Create new post
        blog_posts[slug] = {
            "title": f"New Post: {slug.replace('-', ' ').title()}",
            "content": "This is a new blog post!",
            "author": "Anonymous",
            "tags": ["new"],
        }
        return {"message": "Blog post created", "slug": slug, "post": blog_posts[slug]}
    else:
        # Update existing post
        blog_posts[slug]["content"] = "This post has been updated!"
        return {"message": "Blog post updated", "slug": slug, "post": blog_posts[slug]}
