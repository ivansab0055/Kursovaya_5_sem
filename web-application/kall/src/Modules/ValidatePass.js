import React from "react";

const validatePassword = (password) => {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasCyrillic = /[А-Яа-яЁё]/.test(password);

    if (password.length < minLength) {
        return `Пароль должен содержать минимум ${minLength} символов.`;
    }
    if (!hasUpperCase) {
        return 'Пароль должен содержать хотя бы одну заглавную букву.';
    }
    if (!hasLowerCase) {
        return 'Пароль должен содержать хотя бы одну строчную букву.';
    }
    if (hasCyrillic) {
        return 'Пароль не должен содержать кириллические символы.';
    }

    return '';
};

export default validatePassword;
