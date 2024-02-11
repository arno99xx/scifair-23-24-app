(() => {

    const width = 320; // We will scale the photo width to this
    let height = 0; // This will be computed based on the input stream
  
    // |streaming| indicates whether or not we're currently streaming
    // video from the camera. Obviously, we start at false.
  
    let streaming = false;
  
    const videoElm = document.querySelector('#video');
    //const canvasElm = document.querySelector("#canvas");
    let canvasElm = null;
    const photoElm = document.getElementById("photo");
  
    const btnFront = document.querySelector('#btn-front');
    const btnBack = document.querySelector('#btn-back');
    const btnTakePhoto = document.querySelector("#btn-take-photo");
  
    let imgForm = document.getElementById("img_form");
  
    const supports = navigator.mediaDevices.getSupportedConstraints();
    if (!supports['facingMode']) {
      alert('Browser Not supported!');
      return;
    }
  
    let stream;
  
    const capture = async facingMode => {
      const options = {
        audio: false,
        video: {
          facingMode,
          zoom: true
        },
      };
  
      try {
        if (stream) {
          const tracks = stream.getTracks();
          tracks.forEach(track => track.stop());
        }
        stream = await navigator.mediaDevices.getUserMedia(options);
      } catch (e) {
        alert(e);
        return;
      }
      videoElm.srcObject = null;
      videoElm.srcObject = stream;
      videoElm.play();
    }
  
  
    videoElm.addEventListener(
      "canplay",
      (ev) => {
        if (!streaming) {
          height = videoElm.videoHeight / (videoElm.videoWidth / width);
  
          if (isNaN(height)) {
            height = width / (4 / 3);
          }
  
          videoElm.setAttribute("width", width);
          videoElm.setAttribute("height", height);
          // canvasElm.setAttribute("width", width);
          // canvasElm.setAttribute("height", height);
          streaming = true;
        }
      },
      false,
    );
  
    btnBack.addEventListener('click', () => {
      capture('environment');
    });
  
    btnFront.addEventListener('click', () => {
      capture('user');
    });
  
    btnTakePhoto.addEventListener(
      "click",
      (ev) => {
        takePicture();
        ev.preventDefault();
      },
      false,
    );
  
    imgForm.onsubmit = (evt) => {
      console.log("onsubmit");
      console.log(photoElm.src.length);
      if (photoElm.src.length <= 10) {
          console.log("nothing to submit");
          evt.preventDefault();
          return false;
      } else {
          let imgContentElm = document.getElementById("img_content");
          imgContentElm.value = photoElm.src;
      }
      //evt.preventDefault();
    };
  
    let fileElm = document.getElementById("fileToUpload");
  
    fileElm.onchange = (evt) => {
          console.log('onchange');
          console.log(evt);
          let files = evt.target.files;
          // FileReader support
          if (FileReader && files && files.length) {
              var fr = new FileReader();
              fr.onload = function () {
                  photoElm.src = fr.result;
                  photoElm.width = width;
                  console.log(`photoElm done.. width=${width}`);
              }
              fr.readAsDataURL(files[0]);
          }
          else {
              // fallback -- perhaps submit the input to an iframe and temporarily store
              // them on the server until the user's session ends.
              console.log("error: failed to load files : not supported");
          }
      };
  
  
    clearPhoto();
  
  
    function clearPhoto() {
      let canvasElm = document.createElement("canvas");
      canvasElm.setAttribute("id", "canvas");
      canvasElm.setAttribute("width", width);
      canvasElm.setAttribute("height", height);
      const context = canvasElm.getContext("2d");
      context.fillStyle = "#AAA";
      context.fillRect(0, 0, canvasElm.width, canvasElm.height);
  
      const data = canvasElm.toDataURL("image/jpeg", 1);
      photoElm.setAttribute("src", data);
    }
  
    // Capture a photo by fetching the current contents of the video
    // and drawing it into a canvas, then converting that to a PNG
    // format data URL. By drawing it on an offscreen canvas and then
    // drawing that to the screen, we can change its size and/or apply
    // other changes before drawing it.
  
    function takePicture() {
      let canvasElm = document.createElement("canvas");
      canvasElm.setAttribute("id", "canvas");
      canvasElm.setAttribute("width", width);
      canvasElm.setAttribute("height", height);
      const context = canvasElm.getContext("2d");
      if (width && height) {
        console.log("takePicture");
        canvasElm.width = width;
        canvasElm.height = height;
        context.drawImage(videoElm, 0, 0, width, height);
  
        const data = canvasElm.toDataURL("image/jpg", 1);
        photoElm.setAttribute("src", data);
        console.log("taken");
      } else {
        clearPhoto();
      }
    }
  
    console.log("init done..");
  })();
  