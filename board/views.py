from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Post
from .forms import PostForm
from django.db.models import Q

# 1. 목록 조회 (페이징 + 역순 번호 + 검색 기능)
def post_list(request):
    posts_list = Post.objects.all().order_by('-created_at')
    
    # 💡 검색 값 가져오기
    search_type = request.GET.get('search_type', '')  # title, content, title_content
    kw = request.GET.get('kw', '')                   # 검색어

    # 💡 검색 필터링
    if kw:
        if search_type == 'title':
            posts_list = posts_list.filter(Q(title__icontains=kw))
        elif search_type == 'content':
            posts_list = posts_list.filter(Q(content__icontains=kw))
        elif search_type == 'title_content':
            posts_list = posts_list.filter(Q(title__icontains=kw) | Q(content__icontains=kw))

    # 한 페이지당 10개씩 노출
    paginator = Paginator(posts_list, 10)
    
    # URL의 ?page=2 값 가져오기
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # 역순 번호 할당
    if posts.paginator.count > 0:
        start_number = posts.paginator.count - (posts.start_index() - 1)
        for idx, post in enumerate(posts):
            post.custom_num = start_number - idx

    return render(request, 'board/post_list.html', {
        'posts': posts,
        'search_type': search_type,  # 👈 검색 타입 전달 (유지용)
        'kw': kw,                    # 👈 검색어 전달 (유지용)
    })

# 2. 상세 보기
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'board/post_detail.html', {'post': post})

# 3. 글 작성
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect('board:post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'board/post_form.html', {'form': form, 'title': '글쓰기'})

# 4. 글 수정
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('board:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'board/post_form.html', {'form': form, 'title': '글 수정'})

# 5. 글 삭제
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('board:post_list')
    return render(request, 'board/post_confirm_delete.html', {'post': post})