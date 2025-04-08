from s3_utils import download_from_s3

if __name__ == '__main__':
    download_from_s3('results/3fa32ced-e033-4923-a626-f82acb579fe7/output.txt', 'py_output.txt')
    download_from_s3('results/041b825e-2efc-47c0-aeed-9000ba3668d0/output.txt', 'cpp_output.txt')
    download_from_s3('results/682d98bc-12fa-4ef8-95f3-83df3c1b4044/output.txt', 'java_output.txt')
    download_from_s3('results/84b1b3f0-8728-490d-8672-2e915664ad55/output.txt', 'go_output.txt')
    download_from_s3('results/77bf0951-0a3d-4940-89a9-a33f27d8d200/output.txt', 'js_output.txt')