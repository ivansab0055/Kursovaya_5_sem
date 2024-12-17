var AWS = require('aws-sdk');

AWS.config.update({
    accessKeyId: "56c93acad0814ed1a7da9cc5469bb6c8",
    secretAccessKey: "e09f00af41e246cb8601da8d4cab8b27"
});

var s3 = new AWS.S3({
    endpoint: "https://kallosus-data-storage.s3.storage.selcloud.ru",
    s3ForcePathStyle: true,
    signatureVersion: 'v4',
    region: "ru-1",
    apiVersion: "latest"
});
const getObjectFromS3 = (bucket, key) => {
    return new Promise((resolve, reject) => {
        s3.getObject(
            {Bucket: bucket, Key: key},
            function (error, data) {
                if (error) {
                    resolve({error: error});
                } else {

                    resolve({
                        data: data,
                        error: null
                    });
                }
            }
        );
    });
};

const getSignedUrl = async (key, expiresIn = 60 * 60 * 24) => {
    const AWS = require('aws-sdk');

// Укажите свой кастомный endpoint
    const s3 = new AWS.S3({
        accessKeyId: '56c93acad0814ed1a7da9cc5469bb6c8',
        secretAccessKey: 'e09f00af41e246cb8601da8d4cab8b27',
        endpoint: "https://s3.storage.selcloud.ru",
        s3ForcePathStyle: true,
        region: "ru-1",
        signatureVersion: 'v4',
        apiVersion: "latest"
    });

// Определите параметры для ссылки
    const params = {
        Bucket: 'kallosus-data-storage', // Ваш бакет
        Key: key, // Путь к вашему файлу
        Expires: expiresIn// Время действия ссылки в секундах (в данном случае 5 минут)
    };

    return new Promise((resolve, reject) => {
        s3.getSignedUrl('getObject', params, (err, url) => {
            if (err) {
                reject(err);
            } else {

                resolve(url);
            }
        });
    });
};

// Usage

const uploadObjectToS3 = async (bucket, key, body, onProgress) => {
    try {
        const params = { Bucket: bucket, Key: key, Body: body };
        const upload = s3.upload(params);

        // Отслеживание прогресса загрузки
        upload.on('httpUploadProgress', (event) => {
            const percentCompleted = Math.round((event.loaded / event.total) * 100);
            if (onProgress) {
                onProgress(percentCompleted); // Передаем процент загрузки через коллбэк
            }
        });

        const data = await upload.promise();
        return { data, error: null };
    } catch (error) {
        return { data: null, error: error.message };
    }
};

const getMimeTypeFromS3 = async (bucket, key) => {
    try {
        const params = {Bucket: bucket, Key: key};
        const data = await s3.headObject(params).promise();
        return {mimeType: data.ContentType, error: null};
    } catch (error) {
        return {mimeType: null, error: error.message};
    }
};

module.exports = {
    getSignedUrl,
    getObjectFromS3,
    uploadObjectToS3,
    getMimeTypeFromS3 // Экспорт новой функции
};
