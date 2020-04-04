from django.conf.urls import patterns, url

from CRM.Processors.IndicatorBook.IndicatorManager import *

urlpatterns = patterns('',
                       url(r'^$', view_all_indicators, name='indicator_view_all'),
                       url(r'^upload/$', upload_indicator_attachment, name='indicator_upload'),
                       url(r'^upload/view/$', view_indicator_file, name='indicator_view_files'),
                       url(r'^add/$', add_new_indicator, name='indicator_add'),
                       url(r'^rm/$', remove_new_indicator, name='indicator_rm'),
                       url(r'^j/$', get_indicator, name='indicator_view_single'),
                       url(r'^pb/$', view_pocket_book, name='indicator_pocket_book_view'),
                       url(r'^pb/add/$', add_pocket_book, name='indicator_pocket_book_add'),
                       url(r'^pb/rm/$', delete_pocket_book, name='indicator_pocket_book_remove'),
                       url(r'^pb/j/$', get_pocket_book, name='indicator_pocket_book_single'),
                       url(r'^lf/$', view_letter_files, name='indicator_letter_file_view'),
                       url(r'^lf/add/$', add_letter_file, name='indicator_letter_file_add'),
                       url(r'^lf/rm/$', delete_letter_file, name='indicator_letter_file_rm'),
                       url(r'^lf/j/$', get_letter_file, name='indicator_letter_file_single'),
                       url(r'^sr/$', set_receive_date, name='indicator_set_receive'),
                       )
