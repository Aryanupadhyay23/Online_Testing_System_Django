from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from OTS.models import *
from django.template import loader
import random




def welcome(request):
    template = loader.get_template('welcome.html')
    return HttpResponse(template.render())

def candidateRegistrationForm(request):
    res = render(request, 'registration_form.html')
    return res

def candidateRegistration(request):
    if request.method == 'POST':
        username = request.POST['username']

        # Check if the user already exists
        if len(Candidate.objects.filter(username=username)):
            userStatus = 1
        else:
            candidate = Candidate()
            candidate.username = username
            candidate.password = request.POST['password']
            candidate.name = request.POST['name']
            candidate.save()
            userStatus = 2

    else:
        userStatus = 3  # Request method is not POST

    context = {
        'userStatus': userStatus
    }

    return render(request, 'registration.html', context)

def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        candidate = Candidate.objects.filter(username=username, password=password)
        if len(candidate) == 0:
            loginError = "Invalid username or password"
            return render(request, 'login.html', {'loginError': loginError})
        else:
            request.session['username'] = username
            request.session['name'] = candidate[0].name
            return HttpResponseRedirect(reverse('OTS:home'))
    else:
        return render(request, 'login.html')

def candidateHome(request):
    if 'name' not in request.session.keys():
        return HttpResponseRedirect(reverse('OTS:login'))
    else:
        return render(request, 'home.html', {'name': request.session['name']})


def testPaper(request):
    if 'name' not in request.session.keys():
        return HttpResponseRedirect(reverse('OTS:login'))

    n = int(request.GET['n'])
    question_pool = list(Question.objects.all())
    random.shuffle(question_pool)
    questions_list = question_pool[:n]
    context = {'questions': questions_list}
    res = render(request, 'test_paper.html', context)
    return res


def calculateTestResult(request):
    if 'name' not in request.session.keys():
        return HttpResponseRedirect(reverse('OTS:login'))

    total_attempt = 0
    total_right = 0
    total_wrong = 0
    qid_list = []

    for k in request.POST:
        if k.startswith('qno'):
            qid_list.append(int(request.POST[k]))

    for n in qid_list:
        question = Question.objects.get(qid=n)
        try:
            if question.ans == request.POST['q' + str(n)]:
                total_right += 1
            else:
                total_wrong += 1

            total_attempt += 1

        except:
            pass

    if len(qid_list) == 0:
        points = 0
    else:
        points = (total_right - total_wrong) / len(qid_list) * 10

    result = Result()
    result.username = Candidate.objects.get(username=request.session['username'])
    result.attempt = total_attempt
    result.right = total_right
    result.wrong = total_wrong
    result.points = points
    result.save()

    candidate = Candidate.objects.get(username=request.session['username'])

    if candidate.test_attempted == 0:
        candidate.points = points
    else:
        candidate.points = (
            candidate.points * candidate.test_attempted + points
        ) / (candidate.test_attempted + 1)

    candidate.test_attempted += 1
    candidate.save()

    return HttpResponseRedirect(reverse('OTS:result'))


def testResultHistory(request):
    if 'name' not in request.session.keys():
        return HttpResponseRedirect(reverse('OTS:login'))

    candidate = Candidate.objects.filter(username=request.session['username'])
    results = Result.objects.filter(username_id=candidate[0].username)
    context = {'candidate': candidate[0], 'results': results}
    res = render(request, 'candidate_history.html', context)
    return res

def showTestResult(request):
    if 'name' not in request.session.keys():
        return HttpResponseRedirect(reverse('OTS:login'))

    result = Result.objects.filter(
        resultid=Result.objects.latest('resultid').resultid,
        username_id=request.session['username']
    )
    context = {'result': result}
    res = render(request, 'show_result.html', context)
    return res

def logoutView(request):
    if 'username' in request.session.keys():
        del request.session['username']
    if 'name' in request.session.keys():
        del request.session['name']
    return HttpResponseRedirect(reverse('OTS:login'))