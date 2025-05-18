import dearpygui.dearpygui as dpg
import dearpygui.demo as demo  # <<< важно!

def main():
    # 1) Создаём контекст
    dpg.create_context()
    # 2) Настраиваем окно
    dpg.create_viewport(title="DPG Demo", width=800, height=600)

    # 3) Показываем встроенное демо из модуля dearpygui.demo
    demo.show_demo()

    # 4) Финализация и запуск
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
