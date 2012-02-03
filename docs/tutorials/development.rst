################################################################################
Development
################################################################################

Local installation
==================

In order to have the local development copies in path, instead of the ones
in the default installation path (eg. ``/usr/lib/python2.6/dist-packages/``),
you could either add the root folders containing your packages
in your ``PYTHONPATH`` in, for example, ``.bashrc``, or you can symlink
the packages inside your "per-user" default Python search path.

That is, use something like::

    mkdir -p ~/.local/lib/python2.6/dist-packages
    ln -s ~/workspace/github_rshk_django-facebook/django_facebook/ ~/.local/lib/python2.6/dist-packages/
    ln -s ~/workspace/github_pythonforfacebook_facebook-sdk/facebook.py ~/.local/lib/python2.6/dist-packages/

.. WARNING::
    For some reason, packages installed in ``~/.local/.../dist-packages``
    take precedence on those inside ``/usr/lib/.../dist-packages`` but **not**
    over those in ``/usr/local/.../dist-packages/``!
    
    Keep this in mind if you installed another version using ``pip``.
