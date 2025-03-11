import WaveFile from 'wavefile';

let recorder, chunks = [];

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorder = new MediaRecorder(stream);

        recorder.ondataavailable = event => {
            chunks.push(event.data);
        };

        recorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/wav' });
            chunks = [];

            // Создаем WAV-файл с помощью WaveFile
            waveFile = new WaveFile();
            waveFile.fromScratch(1, 44100, 32, 16); // Mono, 44.1 kHz, 32-bit float, 16-bit PCM
            waveFile.appendRaw(new Float32Array(blob));

            const wavBuffer = waveFile.toBuffer();
            const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });

            const url = URL.createObjectURL(wavBlob);
            document.getElementById('downloadLink').href = url;
            document.getElementById('downloadLink').download = 'recorded-audio.wav';
            document.getElementById('downloadLink').click();
        };

        recorder.start();

        document.getElementById('recordButton').disabled = true;
        document.getElementById('stopButton').disabled = false;
    } catch (error) {
        console.error('Ошибка при попытке начать запись:', error);
    }
}

// Функция для остановки записи
function stopRecording() {
    if (recorder && recorder.state !== 'inactive') {
        recorder.stop();

        // Меняем доступность кнопок обратно
        document.getElementById('recordButton').disabled = false;
        document.getElementById('stopButton').disabled = true;
    }
}


// При установке пакета через npm, все зависимости помещаются в каталог node_modules. Чтобы правильно импортировать модуль, установленный через npm, необходимо указывать путь относительно каталога node_modules.

// Однако, в контексте браузера, стандартная система модулей JavaScript не может напрямую обращаться к пакету, находящемуся в каталоге node_modules. Потребуется использовать систему сборки, такую как Webpack, Parcel или Rollup, чтобы собрать код и зависимости в единый файл, который можно будет подключить в HTML.

// Решение с использованием Webpack:
// Установить Webpack и его плагины:

// npm install webpack webpack-cli --save-dev
// Создать файл конфигурации Webpack (webpack.config.js):

// const path = require('path');

// module.exports = {
//   entry: './src/main.js', // Указываем точку входа вашего приложения
//   output: {
//     filename: 'bundle.js', // Имя выходного файла
//     path: path.resolve(__dirname, 'dist'), // Каталог для выходных файлов
//   },
//   mode: 'development', // Режим разработки
//   devtool: 'source-map', // Включаем source maps для отладки
// };
// Импортировать модуль в JavaScript файле:

// import WaveFile from 'wavefile';

// // Остальной код остается таким же
// Соберать проект с помощью Webpack:

// npx webpack
// Подключить собранный файл в HTML:

// <script src="dist/bundle.js"></script>


// Альтернативное решение: Использование CDN
// Можно использовать версию модуля, доступную через Content Delivery Network (CDN). Например, если библиотека доступна на CDN, можно подключить её напрямую в HTML:


// <script src="https://cdn.example.com/wavefile.min.js"></script>
// Затем можно использовать модуль в своем коде без необходимости установки через npm и настройки системы сборки.

// При использовании CDN, нужно проверить документацию конкретного CDN-сервиса на наличие актуальной версии и пути к библиотеке.