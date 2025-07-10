from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.shortcuts import redirect
from django.conf import settings
from PIL import Image, ImageEnhance, ImageOps
import sys
import os
import base64
from photopy.codeformer.processor import CodeFormerProcessor
import io
import uuid  
import json

processor = CodeFormerProcessor()


def home(request):
    return render(request, 'Aneality.html')  # karena path-nya sudah di templates/
def show_aneality(request):
    return render(request, 'photopyassets/Aneality.html')
def retake_photos(request):
    request.session.pop('result_photos', None)  # Bersihin session
    return redirect('navtocamera')
def navtocamera(request):
    count = request.GET.get('count', '1')
    return render(request, 'camera.html', {'count': count})
def result_view(request):
    photos = request.session.get('captured_photos', [])
    return render(request, 'result.html', {'photos': photos})
def navtoresult(request):
    import os
    from django.conf import settings

    photo_dir = os.path.join(settings.MEDIA_ROOT, "photos")
    file_list = sorted([
        os.path.join("photos", f) for f in os.listdir(photo_dir)
        if f.endswith('.jpg') or f.endswith('.jpeg')
    ], reverse=True)[:3]  # ambil 3 terakhir aja buat strip 3

    return render(request, 'Result.html', {'photos': file_list})
def result(request):
    enhanced_images = request.session.get('enhanced_images', [])
    return render(request, 'result.html', {'images': enhanced_images})

@csrf_exempt
def save_photos(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            photos = data.get('photos', [])

            saved_photos = []
            photo_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
            os.makedirs(photo_dir, exist_ok=True)

            for idx, base64img in enumerate(photos):
                imgdata = base64img.split(',')[1]
                image_bytes = base64.b64decode(imgdata)
                image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

                filename = f'photo_{idx}.jpg'
                file_path = os.path.join(photo_dir, filename)
                image.save(file_path, format='JPEG', quality=90)

                saved_photos.append(f'/media/photos/{filename}')

            # Simpan ke session biar bisa diakses di Result.html
            request.session['result_photos'] = saved_photos
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})
    return JsonResponse({'status': 'error', 'error': 'Invalid request'})

def apply_frame(request):
    if request.method == 'POST':
        # Ambil data foto + frame dari request
        foto_base64 = request.POST.get('foto')
        frame_name = request.POST.get('frame')  # contoh: 'frame1.png'
        
        # Decode base64 foto
        foto_data = base64.b64decode(foto_base64.split(',')[1])
        foto = Image.open(io.BytesIO(foto_data))
        
        # Load frame dari static
        frame_path = os.path.join(settings.STATIC_ROOT, 'frames', frame_name)
        frame = Image.open(frame_path).convert("RGBA")
        
        # Resize frame sesuai foto (jika perlu)
        frame = frame.resize(foto.size)
        
        # Gabungkan foto + frame
        foto.paste(frame, (0, 0), frame)
        
        # Simpan hasil ke base64
        buffered = io.BytesIO()
        foto.save(buffered, format="JPEG")
        hasil_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return JsonResponse({'hasil': f'data:image/jpeg;base64,{hasil_base64}'})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def apply_mass_filter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            images_data = data.get('images', [])
            filter_type = data.get('filter')

            processed_images = []

            for item in images_data:
                image_data = item.get('image')

                # Clean base64
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                missing_padding = len(image_data) % 4
                if missing_padding:
                    image_data += '=' * (4 - missing_padding)


                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))

                if image.mode != 'RGB':
                    image = image.convert('RGB')

                if filter_type == 'blackwhite':
                    image = ImageOps.grayscale(image).convert('RGB')
                elif filter_type == 'sepia':
                    grayscale = ImageOps.grayscale(image)
                    sepia_pixels = []
                    for pixel in list(grayscale.getdata()):
                        r = min(255, int(pixel * 1.0))
                        g = min(255, int(pixel * 0.8))
                        b = min(255, int(pixel * 0.6))
                        sepia_pixels.append((r, g, b))
                    image = Image.new('RGB', grayscale.size)
                    image.putdata(sepia_pixels)
                elif filter_type == 'vintage':
                    image = ImageEnhance.Brightness(image).enhance(0.8)
                    image = ImageEnhance.Contrast(image).enhance(1.3)
                    vintage_pixels = []
                    for r, g, b in list(image.getdata()):
                        r = min(255, int(r * 1.1))
                        g = min(255, int(g * 1.05))
                        b = min(255, int(b * 0.9))
                        vintage_pixels.append((r, g, b))
                    image.putdata(vintage_pixels)

                # Simpen hasil
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=95)
                processed_image_data = base64.b64encode(buffer.getvalue()).decode()

                processed_images.append({
                    'filename': item.get('filename', 'untitled.jpg'),
                    'image': f'data:image/jpeg;base64,{processed_image_data}'
                })

            return JsonResponse({'success': True, 'images': processed_images})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})