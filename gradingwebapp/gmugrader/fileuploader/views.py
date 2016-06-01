from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.template import loader
from django.shortcuts import render_to_response, render, get_object_or_404 

from django.core.context_processors import csrf

from django.conf import settings

from forms import submissionForm, AssignmentForm, ArticleForm, UserForm, UserProfileForm
from .models import Article, Assignment, Solution 

from django.template import RequestContext
from django.contrib import auth

from django.contrib.auth.decorators import login_required


def computeMetrics (predfile, solfile):
    myPredFile = open (settings.MEDIA_ROOT + str(predfile), 'r')
    #myPredFile = open (settings.MEDIA_ROOT +  '/solution_files/sol.txt', 'r')
    myTrueFile = open (settings.MEDIA_ROOT + str(solfile), 'r')
    predictions = []
    ground      = []
    for predline in myPredFile:
        predictions.append(predline)
    for trueline in myTrueFile:
        ground.append(trueline)
    corr = 0
    for i in range (len(ground)):
        if (ground[i] == predictions[i]):
            corr = corr+1;
            print corr
    myPredFile.close()
    myTrueFile.close()

    return (1.0 * corr)/len(ground)


    
# this is only allowable by the ADMIN/INSTRUCTOR 




def get_accuracy_value (filename):
    myPredFile = open (settings.MEDIA_ROOT + str(filename), 'r')
    #myPredFile = open (settings.MEDIA_ROOT +  '/solution_files/sol.txt', 'r')
    myTrueFile = open (settings.MEDIA_ROOT + '/solution_files/sol.txt', 'r')
    predictions = []
    ground      = []
    for predline in myPredFile:
        predictions.append(predline)
    for trueline in myTrueFile:
        ground.append(trueline)
    corr = 0
    for i in range (len(ground)):
        if (ground[i] == predictions[i]):
            corr = corr+1;
            print corr
    myPredFile.close()
    myTrueFile.close()

    return (1.0 * corr)/len(ground)



def index(request):
    
    form = ArticleForm()
    args = {}
    args.update(csrf(request))

    args['form'] = form

    return render_to_response('fileuploader/create_article.html',args)


def articles(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/fileuploader/login/')
    
    #username = request.POST.get('username')
    #password = request.POST.get('password')
    #user = authenticate(username=username, password=password)
    

    args = {}
    args.update(csrf(request))
    args['articles'] = Article.objects.all()
    return render_to_response('fileuploader/articles.html',args)


#def login(request,user):


def login (request):
    c={}
    c.update(csrf(request))
    return render_to_response('login.html',c)

def auth_view (request):
    username = request.POST.get('username')  
    password = request.POST.get('password')
    user     = auth.authenticate(username=username, password=password)
    print user, username, password 
    if user is not None:
        auth.login(request,user)
        return HttpResponseRedirect('/fileuploader/loggedin')
    else:
        return HttpResponseRedirect('/fileuploader/invalid')


def loggedin(request):
    return render_to_response('loggedin.html', {'full_name': request.user.username})

def invalid_login(request):
    return render_to_response('invalid_login.html')

def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    auth.logout(request)
    return render_to_response('logout.html')



def computescores (request):
    args = {}
    args.update(csrf(request))
    #args['articles'] = Article.objects.filter(title='aaa').update(accuracy=get_accuracy_value(Article.fileshot.filename))
    obj1 = Article.objects.filter(accuracy=0.0)
    for items in obj1:
        items.accuracy = get_accuracy_value (items.fileshot)
        items.save()
    
    args['articles'] = obj1
    return render_to_response('fileuploader/computescores.html', args) 
    
# this is only allowable by the ADMIN/INSTRUCTOR 

def createAssignment (request):
    if request.POST:
        form = AssignmentForm (request.POST, request.FILES)
        if form.is_valid():
            a = form.save()
            return HttpResponseRedirect('viewAssignments.html')
    else:
        form = AssignmentForm()
        args = {}
        args.update(csrf(request))
        args['form'] = form
        return render_to_response('fileuploader/createAssignment.html',args)

@login_required
def submitAssignment (request):
    if request.POST:
        form = submissionForm(request.POST, request.FILES)
        if form.is_valid():
            a = form.save(commit=False)
            a.user = request.user
            print a.user
            a.save()
            # update the counter
            # also update the score
            obj1 = Assignment.objects.filter(name = a.assignment) #.update(uploaded_cnt = uploaded_cnt + 1)
            for items in obj1:
                items.uploaded_cnt = items.uploaded_cnt + 1
                counter = items.uploaded_cnt
                truthFile = items.ground_truth
                items.save()
            # gets all the files back... 
            # we need a table of student - attempts - etc

            obj2 = Solution.objects.filter (assignment = a.assignment)

            for items in obj2:
                if items.solution_file == a.solution_file:
                    items.attempt = counter
                    items.score = computeMetrics (items.solution_file, truthFile)
                    items.save()
            return HttpResponseRedirect('viewSubmissions.html')
    else:
        form = submissionForm()
        args = {}
        args.update(csrf (request))
        args['form'] = form
        return render_to_response('fileuploader/submitAssignment.html',args)


def viewSubmissions (request):
    args = {}
    args.update (csrf (request))
    args['solutions'] = Solution.objects.all ()
    return render_to_response ('fileuploader/viewSubmissions.html', args)


def viewAssignments (request):
    args = {}
    args.update(csrf(request))
    args['assignments'] = Assignment.objects.all()
    return render_to_response('fileuploader/viewAssignments.html',args)


def viewAssignmentsDetail (request,assignment_id):
    args = {}
    args.update (csrf (request))
    assignment  = get_object_or_404 (Assignment, pk = assignment_id)
    args['assignment'] = assignment
    args['submissions'] = Solution.objects.filter (assignment = assignment_id)
    return render (request, 'fileuploader/viewAssignmentsDetail.html', args)  






def create(request):
    if request.POST:
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            a =  form.save()
            return HttpResponseRedirect('/fileuploader/articles.html')
    else:
        form = ArticleForm()

        args = {}
        args.update(csrf(request))
        args['form'] = form
        return render_to_response('fileuploader/create_article.html',args)

def register(request):
    if request.POST:
        uf = UserForm(request.POST, prefix='user')
        upf= UserProfileForm(request.POST, prefix='userprofile')
        if uf.is_valid() * upf.is_valid():
            user = uf.save()
            user.set_password(user.password)    
            user.save()

            userprofile = upf.save(commit=False)
            userprofile.user=user
            userprofile.save()
            return HttpResponseRedirect('/fileuploader/login')
    else:
        uf = UserForm(prefix='user')
        upf= UserProfileForm(prefix='userprofile')
    
    return render_to_response('register.html', dict(userform=uf,userprofileform=upf), context_instance=RequestContext(request))


#user = User.objects.create_user(username=request.POST['login'], password=request.POST['password'])



# Create your views here.
