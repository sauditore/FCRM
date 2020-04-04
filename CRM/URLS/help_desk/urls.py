
from CRM.Processors.HelpDesk.CallHistory.CallManagement import add_new_call
from CRM.Processors.HelpDesk.CallHistory.AddProblem import add_new_problem
from CRM.Processors.HelpDesk.CallHistory.AddSolution import add_new_solution
from CRM.Processors.HelpDesk.CallHistory.CallManagement import get_recent_calls
from CRM.Processors.HelpDesk.CallHistory.ChooseSolutions import choose_solutions
from CRM.Processors.HelpDesk.CallHistory.ViewAllCalls import view_all_calls
from CRM.Processors.HelpDesk.CallHistory.ViewCallDetail import view_call_detail
from CRM.Processors.HelpDesk.CallHistory.ViewProblems import view_all_problems
from CRM.Processors.HelpDesk.CallHistory.ViewSolutions import view_all_solutions
from CRM.Processors.HelpDesk.CreateDepartment import create_department
from CRM.Processors.HelpDesk.CreateTicket import create_ticket
from CRM.Processors.HelpDesk.ShowAllDepartments import show_all_departments
from CRM.Processors.HelpDesk.ShowAllTickets import show_all_tickets
from CRM.Processors.HelpDesk.ShowDetail import show_desk_detail
from django.conf.urls import patterns, url

__author__ = 'Administrator'

urlpatterns = patterns('',
                       url(r'^create/dep/$', create_department, name='create help department'),
                       url(r'^show/desk/$', show_all_tickets, name='show all tickets'),
                       url(r'^create/new/$', create_ticket, name='create new ticket'),
                       url(r'^detail/$', show_desk_detail, name='ticket details'),
                       url(r'^show/dep/$', show_all_departments, name='show all help desk department'),
                       url(r'^call/add/$', add_new_call, name='add_new_call_log'),
                       url(r'^call/problem/add/$', add_new_problem, name='add_new_problem'),
                       url(r'^call/problem/view/$', view_all_problems, name='view_call_problems'),
                       url(r'^call/solution/add/$', add_new_solution, name='add_new_solution'),
                       url(r'^call/solution/view/$', view_all_solutions, name='view_all_solutions'),
                       url(r'^call/problem/choose/$', choose_solutions, name='choose_solutions'),
                       url(r'^call/show/$', view_all_calls, name='view_call_history'),
                       url(r'^call/log/$', view_call_detail, name='view_single_log'),
                       url(r'^call/last/$', get_recent_calls, name='call_get_recent_json')
)