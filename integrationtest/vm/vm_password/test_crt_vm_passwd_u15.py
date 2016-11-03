'''
Creating KVM VM with password set.
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import test_stub


vm = None

root_password_list = ["password", "98765725", "95_aaapcn ", "0", "9876,*&#$%^&**&()+_="]

def test():
    global vm
    test_util.test_dsc('create VM with setting password')

    for root_password in root_password_list:
        test_util.test_dsc("root_password: \"%s\"" %(root_password))
        vm = test_stub.create_vm(vm_name = 'check-login-vm', image_name = "imageName_i_u15", root_password=root_password)
        vm.check()

        if not test_lib.lib_check_login_in_vm(vm.get_vm(), "root", root_password):
            test_util.test_fail("check login with username:%s, password:%s failed" %("root", root_password))

        vm.destroy()
        vm.check()

        vm.expunge()
        vm.check()

    test_util.test_pass('Set password when VM is creating is successful.')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
        vm.expunge()
