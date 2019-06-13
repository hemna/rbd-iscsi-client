=====
Usage
=====

To use RBD iSCSI Client in a project::

    from rbd_iscsi_client import client

    test = client.RBDISCSIClient('username', 'password',
                                 'http://10.0.0.69:5000')

    response, content = test.get_api()

    # print out the API endpoints
    print(content)

    # register an initiator/client with the gateway
    # fill this with /etc/iscsi/inititorname.iscsi
    initiator_iqn = 'iqn.1996-04.de.suse:01:e55123456789'

    # Get the target_iqn from the gateway to populate this
    resp, body = test.get_targets()
    if 'targets' in body:
       target_iqn = body['targets'][0]

    test.create_client(target_iqn, initiator_iqn)

    # create chap creds
    test.set_client_auth(target_iqn, initiator_iqn,
                         username, password)

    # create disk
    test.create_disk(pool, volume_name)
    lun_name = "%s/%s" % (pool, volume_name)
    test.register_disk(target_iqn, lun_name)

    #now export the disk to the initiator
    test.export_disk(target_iqn, initiator_name,
                     pool, volume_name)
