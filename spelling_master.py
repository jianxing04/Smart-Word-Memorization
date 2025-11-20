import sys
import os

# --- 第一部分：跨平台单字符输入类 (Getch) ---
class Getch:
    """
    用于捕获单个按键，无需等待回车。
    兼容 Windows 和 Unix (Linux/Mac)。
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        # 获取按键，如果是特殊键（如方向键），可能需要调用两次
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'): 
            msvcrt.getch() # 忽略功能键的前导码
            return None
        return ch.decode('utf-8', 'ignore')

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# --- 第二部分：核心逻辑 ---

def load_wordbook(book_id):
    """加载单词本文件"""
    filename = f"wordbook{book_id}.txt"
    if not os.path.exists(filename):
        print(f"\n[错误] 找不到文件: {filename}")
        print("请确保在同级目录下创建了该文件，每行一个单词。")
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        # 过滤空行和两端空格
        words = [line.strip() for line in f if line.strip()]
    
    return words

def smart_input(target_word):
    """
    自定义输入函数，支持 Tab 补全和实时回显。
    """
    getch = Getch()
    
    # 初始化：根据需求，默认显示首字母
    # buffer 是用户当前输入的内容
    input_buffer = list(target_word[0]) 
    
    # 打印首字母 (flush确保立即显示)
    sys.stdout.write(target_word[0])
    sys.stdout.flush()
    
    while True:
        char = getch()
        
        # 1. 处理 Enter (回车键)
        # Windows通常是 \r, Unix是 \n，或者两者组合
        if char in ('\r', '\n'):
            sys.stdout.write('\n') # 换行
            return "".join(input_buffer)
        
        # 2. 处理 Tab (补全功能)
        elif char == '\t':
            current_len = len(input_buffer)
            target_len = len(target_word)
            
            # 如果当前长度小于目标单词长度，且当前已输入部分匹配目标单词的前缀
            # (这里为了简化体验，只要按Tab就尝试补全正确的下一个字母)
            if current_len < target_len:
                next_char = target_word[current_len]
                input_buffer.append(next_char)
                sys.stdout.write(next_char)
                sys.stdout.flush()
        
        # 3. 处理 Backspace (退格键)
        # Windows是 \x08, Unix通常是 \x7f
        elif char in ('\x08', '\x7f'):
            if len(input_buffer) > 0:
                input_buffer.pop()
                # 模拟退格视觉效果：退格 -> 打印空格覆盖 -> 再退格
                sys.stdout.write('\b \b')
                sys.stdout.flush()
                
        # 4. 处理普通字符 (只允许输入可见字符)
        elif char and char.isprintable():
            input_buffer.append(char)
            sys.stdout.write(char)
            sys.stdout.flush()
            
        # 5. 处理 Ctrl+C (中断)
        elif char == '\x03':
            sys.exit(0)

def main():
    print("=== 终极背单词程序 (Shell版) ===")
    print("提示：输入时按 <Tab> 键可自动补全下一个字母。\n")
    
    # 需求1: 选择单词本
    book_id = input("请输入单词本编号 (例如输入2代表 wordbook2.txt): ").strip()
    words = load_wordbook(book_id)
    
    if not words:
        return

    print(f"\n开始背诵！共 {len(words)} 个单词。\n" + "-"*30)

    index = 0
    while index < len(words):
        target = words[index]
        
        # 提示用户开始输入
        # 为了美观，我们在同一行显示
        sys.stdout.write(f"[{index+1}/{len(words)}] 请补全: ")
        sys.stdout.flush()
        
        # 调用自定义的智能输入函数
        user_input = smart_input(target)
        
        # 需求3: 比对结果
        if user_input.strip() == target:
            print("\033[92mCorrect!\033[0m") # 绿色文字
            index += 1 # 进入下一个单词
        else:
            print(f"\033[91mWrong.\033[0m 你输入的是: {user_input}，请重新输入。")
            # index 不增加，循环继续，重新输入当前单词

    print("\n" + "="*30)
    print("恭喜！单词本已全部背完。")

if __name__ == "__main__":
    main()