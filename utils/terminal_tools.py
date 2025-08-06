class TerminalTools:
    """
    Class that provides a lot of tool to handle the terminal
    """
    
    @classmethod
    def clear_terminal_line(cls):
        """
        Clean the terminal actual line
        """
        
        # Lazy import to avoid startup overhead (NFR-01)
        import sys
        import shutil
        
        cols = shutil.get_terminal_size().columns
    
        sys.stdout.write('\r' + ' ' * cols + '\r')  # clean