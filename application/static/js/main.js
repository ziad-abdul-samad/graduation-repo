  
        // Handle role selection
        document.addEventListener('DOMContentLoaded', function () {
            const roleOptions = document.querySelectorAll('.role-option');
            const studentFields = document.getElementById('studentFields');
            const supervisorFields = document.getElementById('supervisorFields');
            
            roleOptions.forEach(option => {
                option.addEventListener('click', function () {
                    // Remove active class from all options
                    roleOptions.forEach(opt => opt.classList.remove('active'));
                    
                    // Add active class to clicked option
                    this.classList.add('active');
                    
                    // Show/hide fields based on selected role
                    if (this.dataset.role === 'student') {
                        studentFields.style.display = 'block';
                        supervisorFields.style.display = 'none';
                    } else {
                        studentFields.style.display = 'none';
                        supervisorFields.style.display = 'block';
                    }
                });
            });
        });
    // uplad project
      
        // Image Preview
        document.getElementById('imageInput').addEventListener('change', function(e) {
            const preview = document.getElementById('imagePreview');
            preview.innerHTML = '';
            
            Array.from(e.target.files).forEach(file => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    
                    reader.onload = function(event) {
                        const img = document.createElement('img');
                        img.src = event.target.result;
                        preview.appendChild(img);
                    }
                    
                    reader.readAsDataURL(file);
                }
            });
        });

        // Video Preview
        document.getElementById('videoInput').addEventListener('change', function(e) {
            const preview = document.getElementById('videoPreview');
            preview.innerHTML = '';
            
            if (e.target.files[0]) {
                const file = e.target.files[0];
                const video = document.createElement('video');
                video.src = URL.createObjectURL(file);
                video.controls = true;
                video.className = 'video-preview';
                preview.appendChild(video);
            }
        });

        // PDF Preview
        document.getElementById('pdfInput').addEventListener('change', function(e) {
            const preview = document.getElementById('pdfPreview');
            preview.innerHTML = '';
            
            if (e.target.files[0]) {
                const file = e.target.files[0];
                preview.innerHTML = `
                    <div class="alert alert-success">
                        <i class="bi bi-file-earmark-pdf me-2"></i>
                        تم رفع ملف PDF: ${file.name}
                    </div>
                `;
            }
        });
    