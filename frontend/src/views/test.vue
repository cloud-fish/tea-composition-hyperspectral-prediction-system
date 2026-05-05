<script setup lang="ts">
import FileUpload from '../components/FileUploader.vue'
import NavBar from '../components/NavBar.vue'  
import { Upload, Play, CheckCircle, Loader2, Zap, BarChart3 } from 'lucide-vue-next';

</script>
<template>
    <div>
        <!-- <NavBar /> -->
        <NavBar :uploadedFile="uploadedFile" />
        <h1>分割线</h1>
        <FileUpload />
    </div>
</template>



