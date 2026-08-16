# Live2D
try:
    import live2d.v3 as live2d
    from .addon import v3 as addon
except (OSError, SystemError, ImportError):
    import live2d.v2 as live2d
    from .addon import v2 as addon


def reload(arch):
    global live2d, addon
    live2d.dispose()

    if arch == 3:
        try:
            import live2d.v3 as live2d
            from .addon import v3 as addon
        except (OSError, SystemError, ImportError):
            return False
    else:
        import live2d.v2 as live2d
        from .addon import v2 as addon

    live2d.setLogEnable(False)
    live2d.init()
    return True


live2d.setLogEnable(False)
live2d.init()
