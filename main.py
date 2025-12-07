from src.s import *

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {e}", exc_info=True)


