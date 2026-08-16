import winreg as reg


def register_into_menu(file_extension, menu_name, command):
    """
    将自定义命令添加到指定文件类型的右键菜单中。

    :param file_extension: 文件扩展名
    :param menu_name: 右键菜单显示的名称
    :param command: 点击菜单项时执行的命令
    """
    try:
        key = reg.OpenKey(reg.HKEY_CLASSES_ROOT, file_extension, 0, reg.KEY_ALL_ACCESS)
        file_type_handler, _ = reg.QueryValueEx(key, None)
        reg.CloseKey(key)

        shell_key_path = f"{file_type_handler}\\shell"
        app_key_path = f"{shell_key_path}\\{menu_name}"
        command_key_path = f"{app_key_path}\\command"

        reg.CreateKey(reg.HKEY_CLASSES_ROOT, shell_key_path)
        reg.CreateKey(reg.HKEY_CLASSES_ROOT, app_key_path)
        command_key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, command_key_path)

        reg.SetValue(command_key, '', reg.REG_SZ, command)

        return True
    except:
        return False


def delete_key_tree(key_handle, subkey_path):
    """
    递归删除注册表中的键及其所有子键。
    :param key_handle: 根键（如 HKEY_CLASSES_ROOT）
    :param subkey_path: 要删除的注册表路径
    """
    try:
        key = reg.OpenKey(key_handle, subkey_path, 0, reg.KEY_ALL_ACCESS)

        while True:
            try:
                subkey_name = reg.EnumKey(key, 0)
                delete_key_tree(key_handle, f"{subkey_path}\\{subkey_name}")
            except OSError:
                break

        reg.CloseKey(key)
        reg.DeleteKey(key_handle, subkey_path)
    except:
        return False


def remove_from_menu(file_extension, menu_name):
    """
    从指定文件类型的右键菜单中移除一个命令。
    :param file_extension: 文件扩展名（例如：'.txt'）
    :param menu_name: 要移除的右键菜单显示的名称
    """
    try:
        with reg.OpenKey(reg.HKEY_CLASSES_ROOT, file_extension) as key:
            file_type_handler, _ = reg.QueryValueEx(key, None)

        shell_menu_path = f"{file_type_handler}\\shell\\{menu_name}"

        delete_key_tree(reg.HKEY_CLASSES_ROOT, shell_menu_path)
        return True
    except:
        return False