
# script-server

Script-server is a Web UI for scripts.  

## 激活环境

```python
ssenv\Scripts\activate
```

##  项目目录下执行下列代码,去除github同步代理报错的问题

```python
git config --global --unset http.proxy 
git config --global --unset https.proxy
```

##  将PIP安装镜像源改为清华

```python
修改pip包镜像源 pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

##  生成requirements.txt

安装：

```python
pip install pipreqs
```

使用方法：

```python
pipreqs D:/py/Scancheck --force 
```

优点：pipreqs 会根据你的代码中实际使用的库生成 requirements.txt，而不是列出所有安装的库。这对减少依赖项非常有用。只需要文件的路径,不需要对应脚本的名称

## Build web

If you are making changes to web files, use npm run build or npm run serve

切换到 CD D:\script-server\web-src\ 执行以下命令
npm run serve 生成测试环境
npm run build 生成正式的web文件
生成web文件时,node.js安装V16版本,其他高版本可能会报错,需要安装vue-cli-service

全局安装Vue CLi：

```python
npm install -g @vue/cli
```

在项目目录下安装

```python
npm install @vue/cli-service --save-dev
```

检查是否安装成功
运行以下命令来确认 @vue/cli-service 是否已正确安装：

```shell
npm list @vue/cli-service
```

如果已安装，你应该会看到类似的信息：

your-project-name@1.0.0 /path/to/your/project
└── @vue/cli-service@4.x.x

## Features

For more details check [how to configure a script](https://github.com/bugy/script-server/wiki/Script-config)
or [how to configure the server](https://github.com/bugy/script-server/wiki/Server-configuration)
 
## Requirements

### Server-side

Python 3.7 or higher with the following modules:

* Tornado 5 / 6

Some features can require additional modules. Such requirements are specified in a corresponding feature description.

OS support:

- Linux (main). Tested and working on Debian 10,11
- Windows (additional). Light testing
- macOS (additional). Light testing

### Client-side

Any more or less up to date browser with enabled JS

Internet connection is **not** needed. All the files are loaded from the server.

## Installation

### For production

1. Download script-server.zip file from [Latest release](https://github.com/bugy/script-server/releases/latest) or [Dev release](https://github.com/bugy/script-server/releases/tag/dev)
2. Create script-server folder anywhere on your PC and extract zip content to this folder

(For detailed steps on linux with virtualenv, please see [Installation guide](https://github.com/bugy/script-server/wiki/Installing-on-virtualenv-(linux)))

#### As a docker container

Please find pre-built images here: https://hub.docker.com/r/bugy/script-server/tags  
For the usage please check [this ticket](https://github.com/bugy/script-server/issues/171#issuecomment-461620836)

### For development

1. Clone/download the repository
2. Run 'tools/init.py --no-npm' script

`init.py` script should be run after pulling any new changes

If you are making changes to web files, use `npm run build` or `npm run serve`

## Setup and run

1. Create configurations for your scripts in *conf/runners/* folder (see [script config page](https://github.com/bugy/script-server/wiki/Script-config) for details)

2. Launch launcher.py from script-server folder

Windows command: launcher.py
Linux command: ./launcher.py

3.Add/edit scripts on the admin page

By default, the server will run on http://localhost:5000

### Server config

All the features listed above and some other minor features can be configured in *conf/conf.json* file. 
It is allowed not to create this file. In this case, default values will be used.
See [server config page](https://github.com/bugy/script-server/wiki/Server-configuration) for details

### Admin panel

Admin panel is accessible on admin.html page (e.g. http://localhost:5000/admin.html)

## Logging

All web/operating logs are written to the *logs/server.log*
Additionally each script logs are written to separate file in *logs/processes*. File name format is
{script\_name}\_{client\_address}\_{date}\_{time}.log.

## Testing/demo

Script-server has bundled configs/scripts for testing/demo purposes, which are located in samples folder. You can
link/copy these config files (samples/configs/\*.json) to server config folder (conf/runners).

## Security

I do my best to make script-server secure and invulnerable to attacks, injections or user data security. However to be
on the safe side, it's better to run Script server only on a trusted network.  
Any security leaks report or recommendations are greatly appreciated!

### Shell commands injection

Script server guarantees that all user parameters are passed to an executable script as arguments and won't be executed
under any conditions. There is no way to inject fraud command from a client-side. However, user parameters are not
escaped, so scripts should take care of not executing them also (general recommendation for bash is at least to wrap all
arguments in double-quotes). It's recommended to use typed parameters when appropriate, because they are validated for
proper values and so they are harder to be subject of commands injection. Such attempts would be easier to detect also.

_Important!_ Command injection protection is fully supported for Linux, but _only_ for .bat and .exe files on Windows
