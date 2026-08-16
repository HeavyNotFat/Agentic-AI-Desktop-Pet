<?php

class AesEncryption
{
    private $key;
    private $method = 'AES-256-CBC';

    public function __construct($key) {
        $this->key = substr(hash('sha256', $key, true), 0, 32);
    }

    /**
     * 加密函数
     *
     * @param string $data 需要加密的数据
     * @return string
     */
    public function encrypt($data) {
        $ivlen = openssl_cipher_iv_length($this->method);
        $iv = openssl_random_pseudo_bytes($ivlen);
        $encrypted = openssl_encrypt($data, $this->method, $this->key, OPENSSL_RAW_DATA, $iv);
        return base64_encode($iv . $encrypted);
    }

    /**
     * 解密函数
     *
     * @param string $data 需要解密的数据
     * @return string
     */
    public function decrypt($data) {
        $c = base64_decode($data);
        $ivlen = openssl_cipher_iv_length($this->method);
        $iv = substr($c, 0, $ivlen);
        $ciphertext_raw = substr($c, $ivlen);
        return openssl_decrypt($ciphertext_raw, $this->method, $this->key, OPENSSL_RAW_DATA, $iv);
    }
}