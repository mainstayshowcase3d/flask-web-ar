#!/usr/bin/env python3
"""
Web AR HTML Generator Tool with Flask Web Interface
Creates customized Web AR HTML files for different products via web form
"""

import os
import shutil
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import tempfile
import zipfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'glb', 'usdz', 'png', 'jpg', 'jpeg', 'gif'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_html_content(data):
    """Generate the HTML content with user's data"""
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-9ECC9ZLCEX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-9ECC9ZLCEX');
</script>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['company_name']} | {data['product_name']}</title>

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            overflow: hidden;
        }}

        .container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}

        .button-container-top {{
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
            z-index: 1000;
        }}

        .ar-button, .copy-button, .share-button {{
            padding: 12px 20px;
            border: none;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }}

        .ar-button {{
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        }}

        .copy-button {{
            background: linear-gradient(45deg, #4ecdc4, #45b7b8);
            color: white;
            box-shadow: 0 4px 15px rgba(78, 205, 196, 0.4);
        }}

        .share-button {{
            background: linear-gradient(45deg, #a55eea, #8e44ad);
            color: white;
            box-shadow: 0 4px 15px rgba(165, 94, 234, 0.4);
        }}

        .ar-button:hover, .copy-button:hover, .share-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }}

        .model-container {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 80px 20px 20px;
        }}

        model-viewer {{
            width: 90%;
            height: 70vh;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}

        .footer {{
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .footer-content {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .qr-code {{
            width: 80px;
            height: 80px;
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            flex-shrink: 0;
        }}

        .footer-text {{
            color: white;
            text-align: left;
        }}

        .footer-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 8px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .footer-tagline {{
            font-size: 16px;
            color: #e0e0e0;
            margin-bottom: 12px;
            font-style: italic;
        }}

        .footer-link {{
            color: #4ecdc4;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.3s ease;
            display: block;
            margin-bottom: 8px;
        }}

        .footer-link:hover {{
            color: #ff6b6b;
        }}

        .footer-line {{
            font-size: 12px;
            color: #b0b0b0;
            margin-bottom: 4px;
        }}

        .footer-copyright {{
            font-size: 10px;
            color: #888;
            margin-top: 8px;
        }}

        @media (max-width: 768px) {{
            .button-container-top {{
                flex-direction: column;
                align-items: center;
            }}

            .footer-content {{
                flex-direction: column;
                gap: 20px;
                text-align: center;
            }}

            .footer-text {{
                text-align: center;
            }}

            .footer-title {{
                font-size: 20px;
            }}

            .qr-code {{
                width: 60px;
                height: 60px;
            }}

            model-viewer {{
                width: 95%;
                height: 60vh;
            }}
        }}
    </style>
</head>

<body>
    <div class="container">
        <div class="button-container-top">
            <!-- Custom Activate AR Button -->
            <button id="ar-button" class="ar-button" onclick="triggerAR()">✨ ACTIVATE AR ✨</button>

            <!-- Copy Link and Share Buttons -->
            <button class="copy-button" onclick="copyLink()">📋 Copy Link</button>
            <button class="share-button" onclick="shareLink()">📤 Share</button>
        </div>

        <div class="model-container">
            <!-- Model Viewer -->
            <model-viewer id="model-viewer"
                          src="./{data['glb_filename']}"
                          ios-src="./{data['usdz_filename']}"
                          alt="{data['product_name']}"
                          shadow-intensity="1.5"
                          camera-controls
                          min-camera-orbit="auto 0deg {data['min_distance']}"
                          max-camera-orbit="auto 95deg {data['max_distance']}"
                          camera-target="{data['camera_target']}"
                          auto-rotate
                          loading="lazy"
                          reveal="auto"
                          ar
                          autoplay
                          ar-scale="fixed">
                <button slot="ar-button" id="hidden-ar-button" style="display: none;"></button>
            </model-viewer>
        </div>

        <!-- Footer with QR Code and Text -->
        <footer class="footer">
            <div class="footer-content">
                <img src="{data['qr_image_filename']}" alt="QR Code" class="qr-code">
                <div class="footer-text">
                    <h1 class="footer-title">{data['company_name']} | {data['product_name']}</h1>
                    <p class="footer-tagline">{data['tagline']}</p>
                    <a href="{data['product_url']}" target="_blank" class="footer-link">
                        Visit {data['company_name']} to learn more about this product.
                    </a>
                    <p class="footer-line">Augmented Reality only available on compatible devices.</p>
                    <p class="footer-copyright">COPYRIGHT ©2025 {data['company_name'].upper()} ALL RIGHTS RESERVED.</p>
                </div>
            </div>
        </footer>
    </div>

    <!-- Model Viewer Scripts -->
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <script nomodule src="https://unpkg.com/@google/model-viewer/dist/model-viewer-legacy.js"></script>

    <!-- JavaScript to Detect Device and Set Camera Orbit -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const modelViewer = document.getElementById('model-viewer');
            const arButton = document.getElementById('ar-button');

            // Function to detect if the device is mobile
            function isMobileDevice() {{
                const userAgent = navigator.userAgent || navigator.vendor || window.opera;
                const isMobilePlatform = /Android|iPhone|iPad|iPod/i.test(userAgent);
                const isiPadOS = navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1;

                return isMobilePlatform || isiPadOS;
            }}

            // Apply camera-orbit settings and show/hide AR button based on detection
            if (isMobileDevice()) {{
                arButton.style.display = 'inline-flex'; // Show the button on mobile
                modelViewer.setAttribute('camera-orbit', '{data['camera_orbit']}');
            }} else {{
                arButton.style.display = 'none'; // Hide the button on desktop
                modelViewer.setAttribute('camera-orbit', '{data['camera_orbit']}');
            }}
        }});

        // Trigger AR via the hidden button in model-viewer
        function triggerAR() {{
            const hiddenARButton = document.getElementById('hidden-ar-button');
            hiddenARButton.click(); // Trigger the hidden AR button
        }}

        // Copy link to clipboard
        function copyLink() {{
            const preferredLink = '{data['final_url']}';
            navigator.clipboard.writeText(preferredLink).then(() => {{
                alert('Link copied to clipboard!');
            }}).catch(err => {{
                console.error('Failed to copy: ', err);
            }});
        }}

        // Share link via Web Share API
        function shareLink() {{
            const preferredLink = '{data['final_url']}';
            if (navigator.share) {{
                navigator.share({{
                    title: '{data['company_name']} - {data['product_name']}',
                    text: 'Check out this cool product!',
                    url: preferredLink
                }}).then(() => {{
                    console.log('Thanks for sharing!');
                }}).catch((error) => {{
                    console.error('Error sharing:', error);
                }});
            }} else {{
                alert('Sharing is not supported on this device. Please copy the link instead.');
            }}
        }}
    </script>
</body>
</html>"""
    
    return html_template

@app.route('/')
def index():
    """Main form page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_ar():
    """Handle form submission and generate AR files"""
    try:
        # Get form data
        company_name = request.form.get('company_name', '').strip()
        product_name = request.form.get('product_name', '').strip()
        tagline = request.form.get('tagline', '').strip()
        product_url = request.form.get('product_url', '').strip()
        final_url = request.form.get('final_url', '').strip()
        
        # Camera settings with defaults
        min_distance = request.form.get('min_distance', '2m').strip() or '2m'
        max_distance = request.form.get('max_distance', '5m').strip() or '5m'
        camera_target = request.form.get('camera_target', '0m .8m 0m').strip() or '0m .8m 0m'
        camera_orbit = request.form.get('camera_orbit', '-35deg 75deg 5m').strip() or '-35deg 75deg 5m'
        
        # Validate required fields
        if not all([company_name, product_name, tagline, product_url, final_url]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('index'))
        
        # Handle file uploads
        glb_file = request.files.get('glb_file')
        usdz_file = request.files.get('usdz_file')
        qr_file = request.files.get('qr_file')
        
        if not glb_file or not usdz_file or not qr_file:
            flash('Please upload all required files (GLB, USDZ, and QR code image).', 'error')
            return redirect(url_for('index'))
        
        if not all([allowed_file(f.filename) for f in [glb_file, usdz_file, qr_file]]):
            flash('Invalid file type. Please upload GLB, USDZ, and image files only.', 'error')
            return redirect(url_for('index'))
        
        # Create unique directory for this generation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = secure_filename(company_name.replace(' ', '_').lower())
        safe_product = secure_filename(product_name.replace(' ', '_').lower())
        
        project_dir = os.path.join(GENERATED_FOLDER, f"{safe_company}_{safe_product}_{timestamp}")
        os.makedirs(project_dir, exist_ok=True)
        
        # Save uploaded files
        glb_filename = secure_filename(glb_file.filename)
        usdz_filename = secure_filename(usdz_file.filename)
        qr_filename = secure_filename(qr_file.filename)
        
        glb_file.save(os.path.join(project_dir, glb_filename))
        usdz_file.save(os.path.join(project_dir, usdz_filename))
        qr_file.save(os.path.join(project_dir, qr_filename))
        
        # Prepare data for HTML generation
        data = {
            'company_name': company_name,
            'product_name': product_name,
            'tagline': tagline,
            'product_url': product_url,
            'glb_filename': glb_filename,
            'usdz_filename': usdz_filename,
            'qr_image_filename': qr_filename,
            'min_distance': min_distance,
            'max_distance': max_distance,
            'camera_target': camera_target,
            'camera_orbit': camera_orbit,
            'final_url': final_url
        }
        
        # Generate HTML content
        html_content = generate_html_content(data)
        
        # Save HTML file
        html_filename = f"{safe_company}_{safe_product}_ar.html"
        html_path = os.path.join(project_dir, html_filename)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create a zip file with all assets
        zip_filename = f"{safe_company}_{safe_product}_ar_package.zip"
        zip_path = os.path.join(project_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(html_path, html_filename)
            zipf.write(os.path.join(project_dir, glb_filename), glb_filename)
            zipf.write(os.path.join(project_dir, usdz_filename), usdz_filename)
            zipf.write(os.path.join(project_dir, qr_filename), qr_filename)
        
        flash('AR HTML package generated successfully!', 'success')
        
        # Return download page with file info
        return render_template('download.html', 
                             zip_filename=zip_filename,
                             zip_path=zip_path,
                             data=data,
                             project_dir=project_dir)
    
    except Exception as e:
        flash(f'Error generating AR package: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download generated files"""
    try:
        # Security: Only allow downloads from generated folder
        if not filename.startswith(GENERATED_FOLDER):
            return "Access denied", 403
        
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            flash('File not found.', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Create templates directory and files if they don't exist
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create base template
    base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Web AR Generator{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .container { max-width: 800px; }
        .card { border: none; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        .btn-primary { background-color: #007bff; border-color: #007bff; }
        .form-label { font-weight: 600; }
        .alert { border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    # Create index template
    index_template = """{% extends "base.html" %}

{% block title %}Web AR Generator - Create Your AR Experience{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h3 class="card-title mb-0">Web AR HTML Generator</h3>
                <p class="mb-0">Create customized Web AR experiences for your products</p>
            </div>
            <div class="card-body">
                <form method="POST" action="/generate" enctype="multipart/form-data">
                    
                    <div class="row mb-4">
                        <div class="col-md-12">
                            <h5 class="text-primary">Product Information</h5>
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label for="company_name" class="form-label">Company Name *</label>
                            <input type="text" class="form-control" id="company_name" name="company_name" required>
                        </div>
                        <div class="col-md-6">
                            <label for="product_name" class="form-label">Product Name *</label>
                            <input type="text" class="form-control" id="product_name" name="product_name" required>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="tagline" class="form-label">Product Tagline *</label>
                        <input type="text" class="form-control" id="tagline" name="tagline" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="product_url" class="form-label">Product Webpage URL *</label>
                        <input type="url" class="form-control" id="product_url" name="product_url" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="final_url" class="form-label">Final Hosted URL (for sharing/copying) *</label>
                        <input type="url" class="form-control" id="final_url" name="final_url" required>
                    </div>
                    
                    <hr class="my-4">
                    
                    <div class="row mb-4">
                        <div class="col-md-12">
                            <h5 class="text-primary">Upload Files</h5>
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <label for="glb_file" class="form-label">GLB File (Android) *</label>
                            <input type="file" class="form-control" id="glb_file" name="glb_file" accept=".glb" required>
                        </div>
                        <div class="col-md-4">
                            <label for="usdz_file" class="form-label">USDZ File (iOS) *</label>
                            <input type="file" class="form-control" id="usdz_file" name="usdz_file" accept=".usdz" required>
                        </div>
                        <div class="col-md-4">
                            <label for="qr_file" class="form-label">QR Code Image *</label>
                            <input type="file" class="form-control" id="qr_file" name="qr_file" accept="image/*" required>
                        </div>
                    </div>
                    
                    <hr class="my-4">
                    
                    <div class="row mb-4">
                        <div class="col-md-12">
                            <h5 class="text-primary">Camera Settings (Optional)</h5>
                            <p class="text-muted">Leave blank to use default values</p>
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label for="min_distance" class="form-label">Min Camera Distance</label>
                            <input type="text" class="form-control" id="min_distance" name="min_distance" placeholder="2m">
                        </div>
                        <div class="col-md-6">
                            <label for="max_distance" class="form-label">Max Camera Distance</label>
                            <input type="text" class="form-control" id="max_distance" name="max_distance" placeholder="5m">
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label for="camera_target" class="form-label">Camera Target</label>
                            <input type="text" class="form-control" id="camera_target" name="camera_target" placeholder="0m .8m 0m">
                        </div>
                        <div class="col-md-6">
                            <label for="camera_orbit" class="form-label">Camera Orbit</label>
                            <input type="text" class="form-control" id="camera_orbit" name="camera_orbit" placeholder="-35deg 75deg 5m">
                        </div>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-primary btn-lg">Generate AR Experience</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    # Create download template
    download_template = """{% extends "base.html" %}

{% block title %}Download Your AR Package{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h3 class="card-title mb-0">AR Package Generated Successfully!</h3>
            </div>
            <div class="card-body">
                <div class="alert alert-success">
                    <h5>Your Web AR experience is ready!</h5>
                    <p>Company: <strong>{{ data.company_name }}</strong></p>
                    <p>Product: <strong>{{ data.product_name }}</strong></p>
                    <p>Tagline: <strong>{{ data.tagline }}</strong></p>
                </div>
                
                <div class="mb-4">
                    <h5>Package Contents:</h5>
                    <ul>
                        <li>HTML file with AR functionality</li>
                        <li>GLB model file ({{ data.glb_filename }})</li>
                        <li>USDZ model file ({{ data.usdz_filename }})</li>
                        <li>QR code image ({{ data.qr_image_filename }})</li>
                    </ul>
                </div>
                
                <div class="d-grid gap-2 mb-4">
                    <a href="/download/{{ zip_path }}" class="btn btn-success btn-lg">Download Complete Package</a>
                </div>
                
                <div class="alert alert-info">
                    <h6>Next Steps:</h6>
                    <ol>
                        <li>Extract the ZIP file</li>
                        <li>Upload all files to your web server</li>
                        <li>Make sure the model-viewer scripts are accessible</li>
                        <li>Test the AR functionality on mobile devices</li>
                    </ol>
                </div>
                
                <div class="d-grid gap-2">
                    <a href="/" class="btn btn-primary">Generate Another AR Experience</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    # Write template files with UTF-8 encoding
    with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f:
        f.write(base_template)
    
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template)
    
    with open(os.path.join(templates_dir, 'download.html'), 'w', encoding='utf-8') as f:
        f.write(download_template)
    
    print("Starting Web AR Generator Server...")
    print("Open your browser and go to: http://localhost:5000")
    print("Upload your files and generate AR experiences through the web interface!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
