from django_assets import Bundle, register
DEFAULT_CSS_FILES = [
                     'css/bootstrap.css',
                     'font-awesome/css/font-awesome.css',
                     # 'css/system/Images.css',
                     'css/animate.css',
                     'css/plugins/bootstrap-rtl/bootstrap-rtl.min.css',
                     'css/plugins/toastr/toastr.min.css',
                     'css/plugins/sweetalert/sweetalert.css',
                     'css/system/bootgrid/jquery.bootgrid.min.css',
                     'css/system/select2/select2.min.css',
                     'css/plugins/awesome-bootstrap-checkbox/awesome-bootstrap-checkbox.css',
                     'css/style.css',
                     'css/system/CRM.css']

DEFAULT_JS_FILES = ['js/jquery-2.1.1.js',
                    'js/system/maxlen/bootstrap-maxlength.js',
                    'js/system/price-format/price-format.js',
                    'js/bootstrap.min.js',
                    'js/plugins/metisMenu/jquery.metisMenu.js',
                    'js/plugins/slimscroll/jquery.slimscroll.min.js',
                    'js/inspinia.js',
                    'js/plugins/pace/pace.min.js',
                    'js/plugins/toastr/toastr.min.js',
                    'js/plugins/sweetalert/sweetalert.min.js',
                    'js/system/bootgrid/jquery.bootgrid.min.js',
                    'js/system/select2/select2.full.min.js',
                    'js/system/persianDate.js',
                    'js/system/float/floatlabels.min.js',
                    'js/system/AdvancedGrid.js',
                    'old/js/CRMCommon.js']


default_js = Bundle(*DEFAULT_JS_FILES,
                    filters='jsmin', output='crx.js')
default_css = Bundle(*DEFAULT_CSS_FILES,
                     filters='cssmin', output='css/crm.css')
file_upload_css = Bundle('css/plugins/dropzone/dropzone.css', 'css/plugins/dropzone/basic.css',
                         filters='cssmin', output='css/plugins/dropzone/upl.css')
file_upload_js = Bundle('js/plugins/dropzone/dropzone.js', 'js/system/uploader/Uploader.js',
                        filters='jsmin', output='fup.js')
register('js_all', default_js)
register('css_all', default_css)
register('uploader_css', file_upload_css)
register('uploader_js', file_upload_js)
