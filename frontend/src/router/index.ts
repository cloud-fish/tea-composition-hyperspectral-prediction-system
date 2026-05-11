import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import PestDetectionView from '../views/PestDetectionView.vue';
import TeaHyperspectralPredictionView from '../views/TeaHyperspectralPredictionView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/tea-hyperspectral-prediction',
      name: 'tea-hyperspectral-prediction',
      component: TeaHyperspectralPredictionView
    },
    {
      path: '/pest-detection',
      name: 'pest-detection',
      component: PestDetectionView
    }
  ]
});

export default router;
