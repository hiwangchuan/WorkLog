<template>
  <div class="auth-page">
    <div class="auth-card panel">
      <div class="auth-brand">
        <div class="brand-mark">W</div>
        <div>
          <h1>创建 WorkLog AI 账号</h1>
          <p>注册后即可开始记录工作并生成周报</p>
        </div>
      </div>
      <n-form ref="formRef" :model="form" :rules="rules" @keyup.enter="submit">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="form.username" />
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="form.email" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input v-model:value="form.password" type="password" show-password-on="mousedown" />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="submit">注册并进入</n-button>
      </n-form>
      <div class="auth-footer">
        已有账号？
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useMessage, type FormInst, type FormRules } from "naive-ui";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const formRef = ref<FormInst | null>(null);
const loading = ref(false);
const form = reactive({ username: "", email: "", password: "" });
const rules: FormRules = {
  username: { required: true, min: 3, message: "用户名至少 3 个字符" },
  password: { required: true, min: 6, message: "密码至少 6 个字符" }
};
const auth = useAuthStore();
const router = useRouter();
const message = useMessage();

async function submit() {
  await formRef.value?.validate();
  loading.value = true;
  try {
    await auth.register(form);
    router.push("/dashboard");
  } catch (error: any) {
    message.error(error.response?.data?.message || "注册失败");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.16), transparent 30%),
    linear-gradient(135deg, #f8fafc, #eef2ff);
}

.auth-card {
  width: min(430px, 100%);
  padding: 28px;
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.brand-mark {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #14b8a6);
  border-radius: 12px;
  font-size: 20px;
  font-weight: 800;
}

h1 {
  margin: 0;
  font-size: 24px;
}

p {
  margin: 4px 0 0;
  color: #64748b;
}

.auth-footer {
  margin-top: 18px;
  text-align: center;
}
</style>
