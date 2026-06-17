from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Graph me cycle check karne ke liye Kahn's Algorithm (DAG Verification)
def is_dag(nodes, edges):
    try:
        adj_list = {str(node['id']): [] for node in nodes}
        in_degree = {str(node['id']): 0 for node in nodes}
        
        for edge in edges:
            source = str(edge.get('source'))
            target = str(edge.get('target'))
            if source in adj_list and target in in_degree:
                adj_list[source].append(target)
                in_degree[target] += 1

        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        visited_count = 0
        
        while queue:
            current = queue.pop(0)
            visited_count += 1
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        return visited_count == len(nodes)
    except Exception:
        return False

class PipelineParserHandler(BaseHTTPRequestHandler):
    # CORS Headers handle karne ke liye options endpoint
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'Ping': 'Pong'}).encode('utf-8'))

    def do_POST(self):
        if self.path == '/pipelines/parse':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                body = json.loads(post_data.decode('utf-8'))
                nodes = body.get('nodes', [])
                edges = body.get('edges', [])
                
                response_data = {
                    'num_nodes': len(nodes),
                    'num_edges': len(edges),
                    'is_dag': is_dag(nodes, edges)
                }
                status_code = 200
            except Exception as e:
                response_data = {
                    'num_nodes': 0,
                    'num_edges': 0,
                    'is_dag': False,
                    'error': str(e)
                }
                status_code = 400

            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=PipelineParserHandler, port=8000):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f"🚀 Custom Safe Backend Server running on http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()