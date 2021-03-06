'''

New Integration Test for reinit VM.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    vm = test_stub.create_user_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip 

    cmd = 'touch /root/test-file-for-reinit'
    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 180)
    if rsp == False:
	test_util.test_fail('Fail to create file in VM')

    vm.stop()
    vm.reinit()
    vm.update()
    vm.check()
    vm.start()

    cmd = '[ -e /root/test-file-for-reinit ] && echo yes || echo no'
    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 180)
    if rsp == 'yes':
	test_util.test_fail('VM does not be reverted to image used for creating the VM, the later file still exists')

    vm.destroy()
    test_util.test_pass('Re-init VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
