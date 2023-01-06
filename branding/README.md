1000Farms Branding
==============

Getting Started
---------------

- Activate the FormShare environment.
```
$ . ./path/to/FormShare/bin/activate
```

- Change directory into your newly created plugin.
```
$ cd branding
```

- Build the plugin
```
$ python setup.py develop
```

- Add the plugin to the FormShare list of plugins by editing the following line in development.ini or production.ini
```
    #formshare.plugins = examplePlugin
    formshare.plugins = branding
```

- Run FormShare again
