from math import ceil

from django import http
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from person.models import Post, Reply, ForumCategory, Person
from person.serializers import PostSerializer, LogicalDeletePostSerializer, CommentSerializer, TopicSerializer


class MyPageNumber(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'size'
    page_query_param = 'page'
    max_page_size = None


class PostView(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(methods=['get'], detail=True)
    def getPostList(self, request, *args, **kwargs):
        postList = Post.objects.all().filter(isDeleted=False).order_by('-createdAt')

        count = ceil(postList.count()/3)

        pg = MyPageNumber()

        page_posts = pg.paginate_queryset(queryset=postList, request=request, view=self)

        # postListSerializer = PostSerializer(instance=postList, many=True)
        postListSerializer = PostSerializer(instance=page_posts, many=True)

        for post in postListSerializer.data:
            # print(post['poster'])
            queryUser = Person.objects.get(id=post['poster'])
            # print(queryUser.name)
            post['count'] = count
            post['username'] = queryUser.name

        # print(postListSerializer.data)

        return http.JsonResponse(postListSerializer.data, safe=False)

    @action(methods=['get'], detail=True)
    def getMyPostsList(self, request, poster):
        myPostsList = Post.objects.all().filter(poster_id=poster).filter(isDeleted=False)

        count = ceil(myPostsList.count() / 3)

        pg = MyPageNumber()

        page_myPosts = pg.paginate_queryset(queryset=myPostsList, request=request, view=self)

        myPostListSerializer = PostSerializer(instance=page_myPosts, many=True)

        for myPost in myPostListSerializer.data:
            queryUser = Person.objects.get(id=myPost['poster'])
            myPost['count'] = count
            myPost['username'] = queryUser.name

        return http.JsonResponse(myPostListSerializer.data, safe=False)

    @action(methods=['get'], detail=True)
    def getCurrentPost(self, request, pk):
        currentPost = Post.objects.get(id=pk)

        currentPostSerializer = PostSerializer(instance=currentPost)

        print(currentPostSerializer.data)

        return http.JsonResponse(currentPostSerializer.data, safe=False)

    @action(methods=['delete'], detail=True)
    def deletePost(self, request, pk):
        post_01 = Post.objects.get(id=pk)

        post_02 = Post.objects.get(id=pk)
        post_02.isDeleted = True

        updated_post = LogicalDeletePostSerializer(instance=post_01, data=post_02.__dict__)
        updated_post.is_valid(raise_exception=True)

        updated_post.save()

        return http.HttpResponse(status=204)


class CommentView(ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = CommentSerializer

    @action(methods=['get'], detail=True)
    def getCommentList(self, request, *args, **kwargs):
        post = request.GET.get('post')

        commentList = Reply.objects.all().filter(post_id=post).filter(parent_id=0).filter(isDeleted=False).order_by('-createdAt')
        print(commentList)

        count = ceil(commentList.count() / 3)

        pg = MyPageNumber()

        page_comments = pg.paginate_queryset(queryset=commentList, request=request, view=self)

        commentListSerializer = CommentSerializer(instance=page_comments, many=True)

        for comment in commentListSerializer.data:
            # print(comment)
            query_reply_to_user = Person.objects.get(id=comment['replyTo_id'])
            query_replies_number = Reply.objects.filter(parent_id=comment['id']).count()
            query_current_user_name = Person.objects.get(id=comment['poster'])
            print(query_current_user_name)
            comment['count'] = count
            comment['replyToName'] = query_reply_to_user.name
            comment['replyNumber'] = query_replies_number
            comment['currentName'] = query_current_user_name.name

        # print(commentListSerializer.data)

        return http.JsonResponse(commentListSerializer.data, safe=False)

    @action(methods=['get'], detail=True)
    def getCurrentReplyList(self, request, *args, **kwargs):

        parent_id = request.GET.get('id')

        replyReplyList = Reply.objects.all().filter(parent_id=parent_id).filter(isDeleted=False).order_by('-createdAt')
        # print(replyReplyList)

        count = ceil(replyReplyList.count() / 3)

        pg = MyPageNumber()

        page_reply_reply = pg.paginate_queryset(queryset=replyReplyList, request=request, view=self)

        replyReplyListSerializer = CommentSerializer(instance=page_reply_reply, many=True)

        for replyReply in replyReplyListSerializer.data:
            query_reply_reply_to_user = Person.objects.get(id=replyReply['replyTo_id'])
            query_reply_current_user = Person.objects.get(id=replyReply['poster'])
            replyReply['count'] = count
            replyReply['replyReplyToName'] = query_reply_reply_to_user.name
            replyReply['replyReplyCurrentName'] = query_reply_current_user.name

        # print(commentListSerializer.data)

        return http.JsonResponse(replyReplyListSerializer.data, safe=False)


class TopicView(ModelViewSet):
    queryset = ForumCategory.objects.all()
    serializer_class = TopicSerializer

    @action(methods=['get'], detail=True)
    def getTopicList(self, request, *args, **kwargs):
        topicList = ForumCategory.objects.all()

        topicListSerializer = TopicSerializer(instance=topicList, many=True)

        # print(topicListSerializer.data)

        return http.JsonResponse(topicListSerializer.data, safe=False)