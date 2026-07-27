from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required  # 👈 로그인 권한 체크용
from django.contrib import messages                        # 👈 권한 없음 알림용
from .models import Post
from .forms import PostForm

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
        'search_type': search_type,
        'kw': kw,
    })

# 2. 상세 보기
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'board/post_detail.html', {'post': post})

# 3. 글 작성 (로그인 필수 + 작성자 자동 지정)
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False) # DB에 즉시 저장하지 않고 객체 생성
            post.author = request.user     # 👈 현재 로그인한 유저를 작성자로 입력
            post.save()                    # DB 저장
            return redirect('board:post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'board/post_form.html', {'form': form, 'title': '글쓰기'})

# 4. 글 수정 (로그인 필수 + 본인 확인)
@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 본인이 작성한 글이 아니면 수정 거부
    if request.user != post.author:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('board:post_detail', pk=post.pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('board:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'board/post_form.html', {'form': form, 'title': '글 수정'})

# 5. 글 삭제 (로그인 필수 + 본인 확인)
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 본인이 작성한 글이 아니면 삭제 거부
    if request.user != post.author:
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('board:post_detail', pk=post.pk)

    if request.method == 'POST':
        post.delete()
        return redirect('board:post_list')
    return render(request, 'board/post_confirm_delete.html', {'post': post})