'''
zstack volume test class

@author: Youyk
'''
import zstackwoodpecker.header.header as zstack_header
import zstackwoodpecker.header.header as zstack_header
import zstackwoodpecker.header.volume as volume_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.image as image_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

class ZstackTestVolume(volume_header.TestVolume):
    def __init__(self):
        super(ZstackTestVolume, self).__init__()
        self.volume_creation_option = test_util.VolumeOption()
        self.original_checking_points = []
        self.delete_policy = test_lib.lib_get_delete_policy('volume')
        self.delete_delay_time = test_lib.lib_get_expunge_time('volume')

    def create(self):
        self.set_volume(vol_ops.create_volume_from_offering(self.volume_creation_option))
        super(ZstackTestVolume, self).create()

    def migrate(self, host_uuid, session_uuid = None):
        '''
        Only valid when volume is in local storage
        '''
        vol_ops.migrate_volume(self.get_volume().uuid, host_uuid, session_uuid)

    def create_template(self, backup_storage_uuid_list, name = None):
        image_inv = vol_ops.create_volume_template(self.get_volume().uuid, \
                backup_storage_uuid_list, name)
        image = zstack_image_header.ZstackTestImage()
        image.set_image(image_inv)
        image.set_state(image_header.CREATED)
        super(ZstackTestVolume, self).create_template()
        return image

    def attach(self, target_vm):
	new_volume = vol_ops.attach_volume(self.get_volume().uuid, target_vm.get_vm().uuid)
        if not new_volume:
            test_lib.lib_get_vm_blk_status(target_vm.get_vm())
            #test_util.raise_exeception_no_cleanup('Attach Volume to VM failed with 5 retry.')
            raise test_util.TestError('Attach Volume to VM failed.')
        self.set_volume(new_volume)
        super(ZstackTestVolume, self).attach(target_vm)

    def detach(self, vm_uuid=None):
        #TODO: remove vm_uuid
        if not vm_uuid:
            self.set_volume(vol_ops.detach_volume(self.volume.uuid))
        else:
            self.set_volume(vol_ops.detach_volume(self.volume.uuid, vm_uuid))
        super(ZstackTestVolume, self).detach()

    def delete(self):
        vol_ops.delete_volume(self.volume.uuid)
        super(ZstackTestVolume, self).delete()

    def recover(self):
        vol_ops.recover_volume(self.volume.uuid)
        super(ZstackTestVolume, self).delete()

    def expunge(self):
        vol_ops.expunge_volume(self.volume.uuid)
        super(ZstackTestVolume, self).expunge()

    def clean(self):
        if self.delete_policy != zstack_header.DELETE_DIRECT:
            if self.get_state() == volume_header.DELETED:
                self.expunge()
            elif self.get_state() == volume_header.EXPUNGED:
                pass
            else:
                self.delete()
                self.expunge()
        else:
            self.delete()

    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        self.update()
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestVolume, self).check()

    def set_creation_option(self, volume_creation_option):
        self.volume_creation_option = volume_creation_option

    def get_creation_option(self):
        return self.volume_creation_option

    def update(self):
        if self.state == volume_header.ATTACHED \
                and self.get_target_vm() \
                and (self.get_target_vm().get_state() \
                    == vm_header.DESTROYED \
                    or self.get_target_vm().get_state() \
                    == vm_header.EXPUNGED):
            if self.get_volume().type != 'Root':
                self.set_volume(test_lib.lib_get_volume_by_uuid(self.get_volume().uuid))
                super(ZstackTestVolume, self).detach()
            else:
                super(ZstackTestVolume, self).delete()

    def update_volume(self):
        '''
        Called by snapshot actions, since snapshot action will change volume 
        installPath
        '''
        if self.state != volume_header.EXPUNGED:
            self.set_volume(test_lib.lib_get_volume_by_uuid(self.volume.uuid))

    def set_original_checking_points(self, original_checking_points):
        '''
        If the volume is created from a snapshot, it should inherit snapshot's 
        checking points. Otherwise the previous checking points will lost, when
        create a new snapshot from current volume.
        '''
        self.original_checking_points = original_checking_points

    def get_original_checking_points(self):
        return self.original_checking_points

    def set_delete_policy(self, policy):
        test_lib.lib_set_delete_policy(category = 'volume', value = policy)
        super(ZstackTestVolume, self).set_delete_policy(policy)

    def set_delete_delay_time(self, delay_time):
        test_lib.lib_set_expunge_time(category = 'volume', value = delay_time)
        super(ZstackTestVolume, self).set_delete_delay_time(delay_time)

