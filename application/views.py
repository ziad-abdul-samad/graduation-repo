from django.shortcuts import render , redirect
from django.views.decorators.csrf import csrf_protect
from .models import *
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from itertools import chain
from operator import attrgetter
# Create your views here.

@csrf_protect
def login(request):
    universities = University.objects.all()
    majors = Major.objects.all()
    request.session['email'] = None
    if request.method == 'POST' :
        if request.POST.get("loginBtn") != None :
            email = request.POST.get('email')
            password = request.POST.get('password')
            if Student.objects.filter(email = email).exists():
                if Student.objects.filter(email = email , password = password).exists():
                    request.session['email'] = email 
                    request.session['fullname'] = Student.objects.get(email = email).fullname
                    request.session['userType'] = "student"
                    return redirect('/')
                else :
                    return render(request , 'pages/login.html' , {'msg' : 'the password is not correct' , 'unvs' : universities , 'majors' : majors})
            elif Supervisor.objects.filter(email = email).exists():
                if Supervisor.objects.filter(email = email , password = password).exists():
                    request.session['email'] = email 
                    request.session['fullname'] = Supervisor.objects.get(email = email).fullname
                    request.session['userType'] = "supervisor"
                    return redirect('/')
                else :
                    return render(request , 'pages/login.html' , {'msg' : 'the password is not correct' , 'unvs' : universities, 'majors' : majors})
            else :
                return render(request , 'pages/login.html' , {'msg' : 'the email is not exists' , 'unvs' : universities, 'majors' : majors})
        elif request.POST.get("createAccount") != None:
            userType = request.POST.get('type')
            if userType == 'student':
                StudentFullName = request.POST.get('StudentFullName')
                studentID = request.POST.get('studentID')
                StudentMajor = int(request.POST.get('StudentMajor'))
                graduationYear = int(request.POST.get('graduationYear'))
                StudentUniversity = int(request.POST.get('StudentUniversity'))
                StudentPassword = request.POST.get('password')
                rPassword = request.POST.get('rpassword')
                StudentEmail = request.POST.get('email')
                unvObject = University.objects.get(id = StudentUniversity)
                mjObject = Major.objects.get(id = StudentMajor)
                if StudentPassword == rPassword :
                    if StudentFullName != None and studentID != None and StudentMajor != None and graduationYear != None and StudentUniversity != None and StudentPassword != None and StudentEmail != None:
                        if Supervisor.objects.filter(email = StudentEmail).exists != True :
                            if Student.objects.filter(email = StudentEmail).exists != True:
                                studentObject = Student(fullname = StudentFullName , password = StudentPassword , email = StudentEmail , student_id = studentID ,department = mjObject , grade_year = graduationYear , university = unvObject)                     
                                studentObject.save()
                                StudentDetails(studentID = Student.objects.get(email = StudentEmail)).save()
                                request.session['email'] = StudentEmail 
                                request.session['fullname'] = Student.objects.get(email = StudentEmail).fullname
                                request.session['userType'] = "student"
                                return redirect('/')
            elif userType == 'supervisor':
                SVPassword = request.POST.get('password')
                rPassword = request.POST.get('rpassword')
                SVEmail = request.POST.get('email')
                supervisorName = request.POST.get('supervisorName')
                academicRank = request.POST.get('supervisorPosotion')
                supervisordepartment = request.POST.get('supervisordepartment')
                supervisorUniversity = request.POST.get('supervisorUniversity')
                if rPassword == SVPassword:
                    if SVPassword != None and SVEmail != None and supervisordepartment != None and supervisorName != None and academicRank != None and supervisorUniversity != None:
                        if Student.objects.filter(email = SVEmail).exists != True :
                            if Supervisor.objects.filter(email = SVEmail).exists != True:
                                supervisor = Supervisor(email = SVEmail , fullname = supervisorName , password = SVPassword , position = academicRank , department = Major.objects.get(id = supervisordepartment) , university = University.objects.get(id = supervisorUniversity))
                                supervisor.save()
                                request.session['email'] = SVEmail 
                                request.session['fullname'] = Supervisor.objects.get(email = SVEmail).fullname
                                request.session['userType'] = "supervisor"
                                return redirect('/')
    return render(request , 'pages/login.html' , {'unvs' : universities , 'majors' : majors})

@csrf_protect
def index(request):
    if 'email' in request.session == None:
        request.session['fullname'] = None
        request.session['userType'] = None
        request.session['email'] = None
    universities = University.objects.all()
    majors = Major.objects.all()
    years = [year for year in range(datetime.now().year, datetime.now().year - 6, -1)]
    data = {
        'majors' : majors , 
        'univs' : universities ,
        'fullname' : request.session['fullname'] if 'fullname' in request.session != None else None , 
        'userType' : request.session['userType'] if 'fullname' in request.session != None else None, 
        'email' : request.session['email'] if 'fullname' in request.session != None else None,
        'years' : years ,
    }
    if request.method == 'POST' :
        majorID = int(request.POST.get('majorID'))
        universityID = int(request.POST.get('universityID'))
        yearID = int(request.POST.get('yearID'))
        projects = Projects.objects.filter(MajorID = Major.objects.get(id = majorID) , yearOfProject = yearID , UniversityID = University.objects.get(id = universityID))
        data.update({'projects' : projects})
        request.method = None
    elif (request.POST.get('majorID') == None) or (request.POST.get('universityID') == None) or (request.POST.get('yearID') == None) :
        projects = Projects.objects.all().order_by('id')
        data.update({'projects' : projects})
        request.method = None
    return render(request , 'pages/index.html' , data)

@csrf_protect
def projectDetails(request , id):

    project = Projects.objects.get(id = id)

    Counter = Ratings.objects.filter(ProjectID = project).count()

    SumCreativity = Ratings.objects.filter(ProjectID=project).aggregate(total=Sum('Creativity'))['total'] or 0

    SumImplementation = Ratings.objects.filter(ProjectID=project).aggregate(total=Sum('Implementation'))['total'] or 0

    SumFunctionality = Ratings.objects.filter(ProjectID=project).aggregate(total=Sum('Functionality'))['total'] or 0

    SumInterface = Ratings.objects.filter(ProjectID=project).aggregate(total=Sum('Interface'))['total'] or 0
    try:
        rating = ((SumCreativity / Counter) + (SumImplementation / Counter) + (SumFunctionality / Counter) + (SumInterface / Counter))/4
        project.rates = rating
    except ZeroDivisionError:
        project.rates = 0

    pictures = ProjectPictures.objects.filter(ProjectID = project)

    videos = ProjectMedia.objects.filter(ProjectID = project)

    if 'email' in request.session :
        if request.session['userType'] == 'supervisor':
            if request.method == 'POST':
                if request.POST.get('sendcomment') != None:
                    comment = request.POST.get('comment')
                    Comments(comment = comment , projectID = Projects.objects.get(id = id) , SupervisorID = Supervisor.objects.get(email = request.session['email'])).save()


    data = {
        'project' : project ,
        'Creativity' : (SumCreativity / Counter) if SumCreativity != 0 else 0  ,
        'Implementation' : (SumImplementation / Counter) if SumImplementation != 0 else 0 , 
        'Functionality' : (SumFunctionality / Counter) if SumFunctionality != 0 else 0 ,
        'Interface' : (SumInterface / Counter) if SumInterface != 0 else 0 ,
        'pics' : pictures ,
        'videos' : videos ,
        'user' : request.session['email'] ,
        'userType' : request.session['userType'] ,
        'comments' : Comments.objects.filter(projectID = Projects.objects.get(id = id))
    }
    return render(request , 'pages/Project Details.html' , data)

@csrf_protect
def UploadProject(request):
    if 'email' in request.session:
        if request.session['email']!=None: 
            if request.session['userType'] == 'student':
                user = request.session['email']
                if request.method == "POST":
                    if request.POST.get('uploadTheProject'):
                        ProjectTitle = request.POST.get('ProjectTitle')
                        ProjectType = request.POST.get('ProjectType')
                        graduationYear = request.POST.get('graduationYear')
                        Description = request.POST.get('Description')
                        fullDescription = request.POST.get('fullDescription')
                        videoFile = request.FILES.get('videoFile')
                        ImageFile = request.FILES.getlist('ImageFile')
                        pdfFile = request.FILES.get('PDFFILE')
                        unv = Student.objects.get(email = user).university
                        mjr = Student.objects.get(email = user).department
                        std = Student.objects.get(email = user)
                        if Projects.objects.filter(ProjectName = ProjectTitle , UniversityID = unv , MajorID = mjr , Student_id = std ,
                                                yearOfProject = graduationYear , Description = Description , FullDescription = fullDescription ,
                                                ProjectType = ProjectType ).exists() == False :
                            project = Projects(ProjectName = ProjectTitle , UniversityID = unv , MajorID = mjr , Student_id = std ,
                                                yearOfProject = graduationYear , Description = Description , FullDescription = fullDescription , pdf_file = pdfFile ,
                                                ProjectType = ProjectType)
                            project.save()
                            if Projects.objects.filter(Student_id = Student.objects.get(email = user)).exists() == True :
                                projectid = Projects.objects.filter(Student_id = Student.objects.get(email = user)).last()
                                ProjectMedia(ProjectID = projectid , vedio = videoFile).save()
                                for pic in ImageFile:
                                    ProjectPictures(ProjectID = projectid , image = pic).save()
                return render(request , 'pages/Upload -project.html' , {'user' : Student.objects.get(email = user).fullname})
            else :
                return redirect('/error/')
        else :
            return redirect('/error/')
    else :
        return redirect('/login/')

@csrf_protect
def BrowseProjects(request , type = None):    
    if 'email' in request.session :
        if request.session['email'] != None:
            universities = University.objects.all()
            majors = Major.objects.all()
            years = [year for year in range(datetime.now().year, datetime.now().year - 6, -1)]
            data = {
                    'univs' : universities , 
                    'majors' : majors ,
                    'years' : years ,
                    'email' : request.session['email'] ,
                    'fullname' : request.session['fullname'],
                    'userType' : request.session['userType'],
            }
            if request.method=='POST':
                if request.POST.get('filterSearch') != None:
                    try:
                        major = request.POST.get('major')
                        university = request.POST.get('university')
                        year = request.POST.get('year')
                        if type == None:
                            projects = Projects.objects.filter(MajorID = Major.objects.get(id = major) , yearOfProject = year , UniversityID = University.objects.get(id = university))
                            data['projects'] = projects
                        elif type == 'new': 
                            projects = Projects.objects.filter(MajorID = Major.objects.get(id = major) , yearOfProject = year , UniversityID = University.objects.get(id = university)).order_by('UploadDate')
                            data['projects'] = projects
                        elif type == 'old': 
                            projects = Projects.objects.filter(MajorID = Major.objects.get(id = major) , yearOfProject = year , UniversityID = University.objects.get(id = university)).order_by('-UploadDate')
                            data['projects'] = projects
                        elif type == 'rating' : 
                            projects = Projects.objects.filter(MajorID = Major.objects.get(id = major) , yearOfProject = year , UniversityID = University.objects.get(id = university)).order_by('rates')
                            data['projects'] = projects
                    except : pass
            else :
                if type == None:
                    projects = Projects.objects.all()
                    data['projects'] = projects
                elif type == 'new': 
                    projects = Projects.objects.all().order_by('UploadDate')
                    data['projects'] = projects
                elif type == 'old': 
                    projects = Projects.objects.all().order_by('-UploadDate')
                    data['projects'] = projects
                elif type == 'rating' : 
                    projects = Projects.objects.all().order_by('rates')
                    data['projects'] = projects
                    
            return render(request , 'pages/Browse Projects.html' , data)
        else :
            return redirect('/error/')
    else :
        return redirect('/login/')

def MyProject(request , id = None):
    if 'email' in request.session:
        if request.session['email'] != None:
            if request.session['userType'] == 'student':
                email = request.session['email']
                data = {}
                if Projects.objects.filter(Student_id = Student.objects.get(email = email)).exists() != False:
                    projects = Projects.objects.filter(Student_id = Student.objects.get(email = email))
                    maxRate = projects.order_by('-rates').first()
                    countOfProjects = projects.count()
                    avarageRating = (projects.aggregate(total=Sum('rates'))['total'] or 0)/countOfProjects
                    ratingProjects = Projects.objects.filter(Student_id = Student.objects.get(email = email) , rates__gt = 0).count()
                    data = {
                        'projects' : projects ,
                        'maxRate' : maxRate ,
                        'ava' : avarageRating ,
                        'ratingProj' : ratingProjects , 
                        'notRating' : countOfProjects-ratingProjects ,
                        'countOfprojs' : countOfProjects ,
                        }
                    if id != None:
                        Projects.objects.get(id = id).delete()
                        return redirect('MyProject')
                return render(request , 'pages/myproject.html' , data)
            else :
                return redirect('/error/')
        else :
            return redirect('/error/')
    else :
        return redirect('/error/')

@csrf_protect
def loginForAdmin(request):
    if request.method == 'POST' :
            if request.POST.get("loginBtn") != None :
                email = request.POST.get('email')
                password = request.POST.get('password')
                if AdminUser.objects.filter(email = email).exists():
                    if AdminUser.objects.filter(email = email , password = password).exists():
                        request.session['email'] = email 
                        request.session['fullname'] = AdminUser.objects.get(email = email).fullname
                        request.session['userType'] = "admin"
                        return redirect('/adminDashboard/')
                    else :
                        return render(request , 'pages/login-admin.html' , {'msg' : 'the password is not correct'})    
    return render(request , 'pages/login-admin.html')

@csrf_protect
def AdminDashboard(request , emailDEl = None):
    if 'email' in request.session :
        if request.session['email'] != None:
            if request.session['userType'] == "admin":
                data = {}
                one_day_ago = timezone.now() - timedelta(days=1)
                twohoursago = timezone.now()-timedelta(hours=2)
                oneWeekAgo = timezone.now() - timedelta(days=7)
                ############## users #############
                countOfUsers = Student.objects.all().count() + Supervisor.objects.all().count() + AdminUser.objects.all().count()
                data['countOfUsers'] = countOfUsers
                countOfStudents = Student.objects.all().count() + Supervisor.objects.all().count()
                data['countOfStudents'] = countOfStudents
                countOfSuperVisors =  Supervisor.objects.all().count()
                data['countOfSupervisor'] = countOfSuperVisors 
                countOfAdmins =  AdminUser.objects.all().count()
                data['countOfAdmins'] = countOfAdmins    
                ############# projects ############           
                countOfProjects = Projects.objects.all().count()
                data['countOfProjects'] = countOfProjects
                countOfNewProjects = Projects.objects.filter(UploadDate__lt=one_day_ago).count()
                data['countOfNewProjects'] = countOfNewProjects
                countOfRatedProjects = Projects.objects.filter(rates__gt = 0).count()
                data['countOfRatedProjects'] = countOfRatedProjects
                countOfProjectsStillRating = countOfProjects - countOfRatedProjects
                data['countOfProjectsStillRating'] = countOfProjectsStillRating
                ############# universities ########
                countOfUniversities = University.objects.all().count()
                data['countOfUniversities'] = countOfUniversities
                universities_with_projects_count = University.objects.filter(projects__isnull=False).distinct().count()
                data['universities_with_projects_count'] = universities_with_projects_count
                ############ ratings ##############
                countOfRatings = Ratings.objects.all().count()
                data['countOfRatings'] = countOfRatings
                averageOfRating = Projects.objects.filter(rates__gt = 0).aggregate(total=Sum('rates'))['total'] or 0
                data['averageOfRating'] = averageOfRating/countOfRatedProjects if averageOfRating > 0 else 0
                StudentsBeforTwoHours = Student.objects.filter(created_at__gt = twohoursago)
                SupervisorBeforTwoHours = Supervisor.objects.filter(created_at__gt = twohoursago)
                ProjectsBeforTwoHours = Projects.objects.filter(UploadDate__gt = twohoursago)
                RatingsBeforTwoHours = Ratings.objects.filter(created_at__gt = twohoursago)
                commentsBeforTwoHours = Comments.objects.filter(created_at__gt = twohoursago)
                for s in StudentsBeforTwoHours:
                    s.type = 'Student'
                for s in SupervisorBeforTwoHours :
                    s.type = "SuperVisor"
                for p in ProjectsBeforTwoHours:
                    p.type = 'Project'
                    p.created_at = p.UploadDate  # توحيد اسم حقل التاريخ
                for r in RatingsBeforTwoHours:
                    r.type = 'Rating'
                for c in commentsBeforTwoHours:
                    c.type = 'Comment'
                all_records = list(chain(StudentsBeforTwoHours,SupervisorBeforTwoHours , ProjectsBeforTwoHours, RatingsBeforTwoHours, commentsBeforTwoHours))
                sorted_records = sorted(all_records, key=attrgetter('created_at'), reverse=True)

                students = Student.objects.filter(created_at__gt = one_day_ago)
                supervisor = Supervisor.objects.filter(created_at__gt = one_day_ago)
                for s in students:
                    s.type = 'student'
                for s in supervisor:
                    s.type = 'supervisor'                
                allUsers = list(chain(students , supervisor))
                ########### return ################
                if request.method == 'POST':
                    fullname = request.POST.get('fullname')
                    email = request.POST.get('email')
                    password = request.POST.get('password')
                    rpassword = request.POST.get('rpassword')
                    if fullname != None and email != None and password != None and rpassword != None:
                        if password == rpassword:
                            if AdminUser.objects.filter(email = email).exists() != True:
                                AdminUser(fullname = fullname , password = password , email = email).save()
                if emailDEl != None:
                    if Student.objects.filter(email = emailDEl).exists() != False:
                        Student.objects.get(email = emailDEl).delete()
                    elif Supervisor.objects.filter(email = emailDEl).exists() != False:
                        Supervisor.objects.get(email = emailDEl).delete()
                    return redirect('/adminDashboard/')
                return render(request , 'pages/Admin Dashboard.html' , {'data' : data , 'records' : sorted_records , 'userRecords' : allUsers})
            else :
                return redirect('/error/')
        else : 
            return redirect('/error/')
    else :
        return redirect('/login/')

@csrf_protect
def studentProfile(request):
    if 'email' in request.session :
        if request.session['email'] != None:
            if request.session['userType'] == 'student':
                user = request.session['email']
                data = {}
                student = Student.objects.get(email = user)
                projects = Projects.objects.filter(Student_id = student)
                if request.method == 'POST':
                    skills = request.POST.get('skills')
                    note = request.POST.get('note')
                    currentPassword = request.POST.get('currentPassword')
                    newPassword = request.POST.get('newPassword')
                    sure = request.POST.get('sure')
                    if note != None:
                        if StudentDetails.objects.filter(studentID = student).exists()!= True:
                            StudentDetails(studentID = student , notes = note).save()
                        else :
                            if note != None:
                                detail = StudentDetails.objects.get(studentID = student)
                                detail.notes = note
                                detail.save()
                    if skills != None:
                        if StudentDetails.objects.filter(studentID = student).exists()== True:
                            detail = StudentDetails.objects.get(studentID = student)
                            skill = skills.split(',')
                            for s in skill:
                                if Skills.objects.filter(skill = s , StudentDetail = detail).exists() != True :
                                    Skills(StudentDetail = detail , skill = s).save()
                        else :
                            StudentDetails(studentID = student , notes = None).save()
                            skill = skills.split(',')
                            for s in skill:
                                Skills(StudentDetail = detail , skill = s).save()
                    if currentPassword != None and newPassword != None and sure != None :
                        if Student.objects.filter(email = user , password = currentPassword).exists() == True :
                            if newPassword == sure :
                                student.password = newPassword
                data = {
                    'user' : student,
                    'projects' : projects ,
                    'notes' : StudentDetails.objects.get(studentID = student).notes ,
                    'skills' : Skills.objects.filter(StudentDetail = StudentDetails.objects.get(studentID = student)) ,
                    'countOfProjects' : projects.count()
                }
                return render(request , 'pages/Student Profile.html' , data)
            else :
                return redirect('/error/')
        else :
            return redirect('/error/')
    else :
        return redirect('/login/')

@csrf_protect
def supervisorDashboard(request):
    if 'email' in request.session:
        if request.session['email'] != None:
            if request.session['userType'] == 'supervisor':
                years = [year for year in range(datetime.now().year, datetime.now().year - 6, -1)]
                data = {
                    'majors' : Major.objects.all() ,
                    'years' : years 
                    }
                user = Supervisor.objects.get(email = request.session['email'])
                univ = Projects.objects.filter(UniversityID = user.university)
                data['projects'] = univ
                if request.method == 'POST':
                    if request.POST.get('saveRating') != None:
                        projectid = request.POST.get('projectid')
                        Creativity = request.POST.get('Creativity')
                        Implementation = request.POST.get('Implementation')
                        Functionality = request.POST.get('Functionality')
                        Interface = request.POST.get('Interface')
                        notes = request.POST.get('notes')
                        degree = request.POST.get('degree')
                        if notes != None :
                            Ratings(Creativity =Creativity ,Implementation = Implementation , Functionality = Functionality , Interface = Interface ,
                                     ProjectID = Projects.objects.get(id = projectid) , notes = notes , SupervisorID = user).save()
                            Projects.objects.get(id = projectid).degree = degree
                        else :
                            Ratings(Creativity =Creativity ,Implementation = Implementation , Functionality = Functionality , Interface = Interface ,
                                     ProjectID = Projects.objects.get(id = projectid) , notes = notes , SupervisorID = user).save()
                            Projects.objects.get(id = projectid).degree = degree
                    elif request.POST.get('search') != None:
                        major = int(request.POST.get('majorID'))
                        year = int(request.POST.get('yearID'))
                        if major == None:
                            projects = Projects.objects.filter(UniversityID = user.university , yearOfProject = year )
                            data['projects'] = projects
                        if year == None:
                            projects = Projects.objects.filter(UniversityID = user.university , MajorID = Major.objects.get(id = major))
                            data['projects'] = projects
                return render(request , 'pages/Supervisor Dashboard.html' , data)
            else :
                return redirect('/error/')
        else :
            return redirect('/error/')
    else :
        return redirect('/login/')

@csrf_protect
def ProjectEvaluationForm(request , id):
    if 'email' in request.session:
        if request.session['email'] != None:
            if request.session['userType'] == 'supervisor':
                project = Projects.objects.get(id = id)
                data = {}
                data['project'] = Projects.objects.get(id = id)
                if request.method == 'POST':
                    Creativity = request.POST.get('Creativity')
                    Implementation = request.POST.get('Implementation')
                    Functionality = request.POST.get('Functionality')
                    Interface = request.POST.get('Interface')
                    degree = int(request.POST.get('degree'))
                    classfication = request.POST.get('classfication')
                    status = request.POST.get('status')
                    notes = request.POST.get('notes')
                    Ratings(Creativity=Creativity , Implementation=Implementation ,Functionality=Functionality , Interface=Interface , ProjectID = project ,
                             notes=notes , SupervisorID = Supervisor.objects.get(email = request.session['email'])).save()
                    if classfication != None:
                        project.classfication = classfication
                    if degree != None:
                        project.degree = degree
                    if status != None:
                        project.status = status
                    project.save()
                return render(request , 'pages/Project Evaluation Form.html' , data)
            else :
                return redirect('/error/')
        else :
            return redirect('/error/')
    else :
        return redirect('/login/')

def logout(request):
    request.session.flush()
    return redirect('/')

def error_404(request):
    return render(request , 'pages/error.html')
def hello_world(request):
    return render(request, 'pages/hello_world.html')
def student_requests(request):
    return render(request, 'pages/student_requests.html')