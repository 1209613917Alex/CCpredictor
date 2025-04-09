import Get_code_metrics
import Get_cloned_code_metrics
import Get_Halstead_metrics
import Label_defective_files

def main():
    Get_code_metrics.main()
    Get_cloned_code_metrics.main()
    Get_Halstead_metrics.main()
    Label_defective_files.main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Process interrupted by user.")