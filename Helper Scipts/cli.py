import argparse
from .composer import compose_flow

def compose_run():
    p = argparse.ArgumentParser()
    p.add_argument('--prompt', '-p', required=False, default='A test prompt')
    p.add_argument('--model', '-m', default=None)
    args = p.parse_args()
    path, flow = compose_flow(args.prompt, model_key=args.model)
    print('Composed flow at', path)

if __name__ == '__main__':
    compose_run()
