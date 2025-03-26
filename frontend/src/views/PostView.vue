<template>
  <div class="grid grid-cols-12 gap-6">
    <!-- 좌측 카테고리 트리 -->
    <div class="col-span-3">
      <CategoryTree />
      <!-- 세로형 광고 추가 -->
      <AdDisplay
        ad-slot="YOUR_VERTICAL_AD_SLOT"
        position="vertical"
        format="vertical"
      />
    </div>
    
    <!-- 중앙 콘텐츠 -->
    <div class="col-span-7">
      <div v-if="loading" class="flex justify-center items-center h-96">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
      
      <div v-else-if="error" class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>
      
      <div v-else class="bg-white shadow rounded-lg p-6">
        <!-- 상단 메타데이터 -->
        <div class="mb-8">
          <div class="flex flex-wrap items-center text-sm text-gray-500 mb-2">
            <div class="flex items-center mr-6">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              <span class="text-blue-600">{{ formatCategory(post.category) }}</span>
            </div>
            
            <div class="flex items-center mr-6">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ formatDate(post.updated_at) }}</span>
            </div>
            
            <div class="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              <span>{{ post.author }}</span>
            </div>
          </div>
          
          <h1 class="text-3xl font-bold text-gray-900">{{ post.title }}</h1>
        </div>
        
        <!-- 상단 광고 -->
        <AdDisplay
          ad-slot="YOUR_HORIZONTAL_AD_SLOT_1"
          position="horizontal"
        />
        
        <!-- 포스트 본문 -->
        <div class="prose max-w-none" v-html="renderedContent"></div>
        
        <!-- 하단 광고 -->
        <AdDisplay
          ad-slot="YOUR_HORIZONTAL_AD_SLOT_2"
          position="horizontal"
        />
        
        <!-- 하단 네비게이션 - 시각적으로 개선된 UI -->
        <div class="mt-12 pt-8 border-t border-gray-200">
          <div class="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-6">
            <!-- 이전 글 링크 -->
            <div class="w-full md:w-1/2">
              <RouterLink 
                v-if="previousPost && previousPost.path"
                :to="`/post/${previousPost.path}`" 
                class="block p-4 bg-gray-50 hover:bg-blue-50 rounded-lg border border-gray-200 hover:border-blue-200 transition-all duration-200"
              >
                <div class="flex items-center text-gray-500 text-sm mb-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                  <span class="font-semibold">이전 글</span>
                </div>
                <div class="font-medium text-gray-900 hover:text-primary line-clamp-2">{{ previousPost.title }}</div>
                <div class="text-xs text-gray-500 mt-1">{{ formatDate(previousPost.updated_at) }}</div>
              </RouterLink>
              <div v-else class="p-4 bg-gray-50 rounded-lg border border-gray-200 text-gray-400 flex items-center justify-center h-[88px]">
                <span class="text-sm">이전 글이 없습니다</span>
              </div>
            </div>
            
            <!-- 다음 글 링크 -->
            <div class="w-full md:w-1/2">
              <RouterLink 
                v-if="nextPost && nextPost.path"
                :to="`/post/${nextPost.path}`" 
                class="block p-4 bg-gray-50 hover:bg-blue-50 rounded-lg border border-gray-200 hover:border-blue-200 transition-all duration-200"
              >
                <div class="flex items-center justify-end text-gray-500 text-sm mb-1">
                  <span class="font-semibold">다음 글</span>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <div class="text-gray-900 font-medium hover:text-primary text-right line-clamp-2">{{ nextPost.title }}</div>
                <div class="text-xs text-gray-500 mt-1 text-right">{{ formatDate(nextPost.updated_at) }}</div>
              </RouterLink>
              <div v-else class="p-4 bg-gray-50 rounded-lg border border-gray-200 text-gray-400 flex items-center justify-center h-[88px]">
                <span class="text-sm">다음 글이 없습니다</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 우측 사이드바 -->
    <div class="col-span-2">
      <div class="bg-white shadow rounded-lg p-6 sticky top-6">
        <!-- 목차 섹션 -->
        <div v-if="hasToc" class="mb-6">
          <h2 class="text-lg font-semibold mb-4">목차</h2>
          <div class="toc-container max-h-60 overflow-y-auto pr-2 text-sm">
            <div v-html="tocHtml" class="toc-links"></div>
          </div>
        </div>
        
        <!-- 동일 카테고리 게시물 -->
        <div class="mb-6">
          <h2 class="text-lg font-semibold mb-4">동일 카테고리</h2>
          <div v-if="loading" class="text-sm text-gray-500">로딩 중...</div>
          <div v-else-if="!categorySiblings.length" class="text-sm text-gray-500">게시물이 없습니다</div>
          <ul v-else class="space-y-2">
            <li v-for="siblingPost in categorySiblings" :key="siblingPost.path" class="text-sm">
              <router-link 
                :to="`/post/${siblingPost.path}`" 
                :class="siblingPost.path === post?.path ? 'text-primary font-medium' : 'text-gray-700 hover:text-primary'"
              >
                {{ siblingPost.title }}
              </router-link>
            </li>
          </ul>
        </div>
        
        <!-- 추천 게시물 -->
        <div>
          <h2 class="text-lg font-semibold mb-4">추천 게시물</h2>
          <ul class="space-y-2">
            <li v-for="recommendPost in recommendedPosts" :key="recommendPost.id" class="text-sm">
              <router-link :to="`/post/${recommendPost.path}`" class="text-gray-700 hover:text-primary">
                {{ recommendPost.title }}
              </router-link>
            </li>
          </ul>
        </div>
        
        <!-- 우측 광고 -->
        <AdDisplay
          ad-slot="YOUR_VERTICAL_AD_SLOT_2"
          position="vertical"
          format="vertical"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { usePostsStore } from '../store/posts'
import CategoryTree from '../components/CategoryTree.vue'
import CategoryList from '../components/CategoryList.vue'
import AdDisplay from '../components/AdDisplay.vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'
import { trackPostView } from '../utils/analytics'
import { trackNaverPostView } from '../utils/naverAnalytics'
import api from '../utils/api'

const route = useRoute()
const postsStore = usePostsStore()

const post = ref(null)
const previousPost = ref(null)
const nextPost = ref(null)
const loading = ref(true)
const error = ref(null)
const mermaidCharts = ref([])
const renderedContent = ref('')
const categorySiblings = ref([])
const tocHtml = ref('')
const hasToc = ref(false)

// 추천 게시물 목록 - 인기 게시물 등 정적 데이터 (실제로는 서버에서 가져옵니다)
const recommendedPosts = ref([
  { id: 1, title: '객체지향 프로그래밍의 기본 원칙', path: 'sw/0090.object-oriented-methodology' },
  { id: 2, title: '코드 스멜이란?', path: 'sw/0048.code-smell' },
  { id: 3, title: '클린 코드의 핵심 원칙', path: 'sw/0091.clean-code' },
  { id: 4, title: '디자인 패턴 개요', path: 'sw/0092.design-patterns' },
  { id: 5, title: '애자일 방법론의 이해', path: 'sw/0093.agile-methodology' }
])

// 다이어그램 확대/축소를 위한 상태
const expandedDiagramId = ref(null);

// 다이어그램 확대 함수
function expandDiagram(id, code) {
  // 기능 제거
  return;
}

// 다이어그램 축소 함수
function shrinkDiagram() {
  // 기능 제거
  return;
}

// 마크다운을 HTML로 변환하고 Mermaid 다이어그램 처리
function processMarkdown(content) {
  if (!content) return '';
  
  // 목차(TOC) 생성을 위한 처리
  const tocContent = generateToc(content);
  tocHtml.value = tocContent.tocHtml;
  hasToc.value = tocContent.hasToc;
  
  // mermaid 코드 블럭 처리를 위한 특별 처리
  const mermaidBlocks = [];
  let processedContent = content.replace(/```mermaid\s+([\s\S]*?)```/g, (match, mermaidCode) => {
    const id = `mermaid-diagram-${Date.now()}-${mermaidBlocks.length}`;
    mermaidBlocks.push({
      id,
      code: mermaidCode.trim()
    });
    return `<div class="mermaid-placeholder" data-index="${mermaidBlocks.length - 1}"></div>`;
  });
  
  // marked 설정 - 최신 버전 호환성
  const renderer = new marked.Renderer();
  
  // 코드 블록 하이라이팅 설정
  renderer.code = function(code, language) {
    if (language === 'mermaid') {
      // 이미 위에서 처리했으므로 여기서는 무시
      return `<pre class="language-mermaid">${code}</pre>`;
    }
    
    const validLanguage = language && hljs.getLanguage(language) ? language : '';
    const highlighted = validLanguage ? 
      hljs.highlight(code, { language: validLanguage }).value : 
      hljs.highlightAuto(code).value;
      
    return `<pre><code class="hljs ${validLanguage}">${highlighted}</code></pre>`;
  };
  
  // marked 옵션 설정 (deprecated 경고 제거)
  marked.use({ 
    renderer,
    gfm: true, 
    breaks: false,
    pedantic: false,
    sanitize: false
  });
  
  // 마크다운을 HTML로 변환
  let html = marked.parse(processedContent);
  
  // mermaid 플레이스홀더를 실제 mermaid 태그로 다시 교체
  mermaidBlocks.forEach((block, index) => {
    const placeholder = `<div class="mermaid-placeholder" data-index="${index}"></div>`;
    html = html.replace(placeholder, 
      `<div class="mermaid-wrapper">
        <div class="mermaid" id="${block.id}" data-diagram-code="${encodeURIComponent(block.code)}">${block.code}</div>
       </div>`
    );
  });
  
  // HTML 정화 - SVG 관련 태그와 속성 모두 허용
  const sanitizedHtml = DOMPurify.sanitize(html, {
    ADD_TAGS: ['div', 'svg', 'path', 'g', 'marker', 'defs', 'polygon', 'foreignObject', 'rect', 'style', 'line', 'circle', 'text', 'textPath', 'linearGradient', 'stop', 'ellipse', 'polyline', 'filter', 'feGaussianBlur', 'feOffset', 'feFlood', 'feComposite', 'feColorMatrix', 'use', 'image', 'pattern', 'clipPath', 'mask', 'pre'],
    ADD_ATTR: ['class', 'id', 'viewBox', 'd', 'fill', 'stroke', 'stroke-width', 'x', 'y', 'width', 'height', 'xmlns', 'xmlns:xlink', 'xlink:href', 'font-size', 'font-family', 'text-anchor', 'dominant-baseline', 'marker-end', 'marker-start', 'points', 'transform', 'style', 'refX', 'refY', 'orient', 'markerWidth', 'markerHeight', 'cx', 'cy', 'r', 'stroke-dasharray', 'stop-color', 'offset', 'rx', 'ry', 'font-weight', 'text-width', 'letter-spacing', 'data-index', 'data-diagram-code']
  });
  
  console.log(`${mermaidBlocks.length}개의 Mermaid 다이어그램 코드 블록을 발견했습니다.`);
  
  // 렌더링을 위해 mermaidBlocks 저장
  mermaidCharts.value = mermaidBlocks;
  
  return sanitizedHtml;
}

// 목차 생성 함수
function generateToc(content) {
  // 헤더를 찾기 위한 정규식
  const headingRegex = /^(#{2,6})\s+(.+)$/gm;
  let match;
  const headings = [];
  let hasToc = false;
  
  // 헤딩 추출
  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length; // #의 개수
    const text = match[2].trim();
    
    // 헤딩에서 ID 생성 (anchor를 위한)
    const id = text.toLowerCase()
      .replace(/[^\w\s-]/g, '') // 영문자, 숫자, 공백, 하이픈이 아닌 문자 제거
      .replace(/\s+/g, '-'); // 공백을 하이픈으로 변환
    
    headings.push({
      level,
      text,
      id
    });
    hasToc = true;
  }
  
  // TOC HTML 생성
  let tocHtml = '';
  let prevLevel = 0;
  
  headings.forEach(heading => {
    if (heading.level > prevLevel) {
      // 레벨이 깊어질 때 새 UL 태그 추가
      for (let i = prevLevel; i < heading.level; i++) {
        tocHtml += '<ul class="pl-4 mt-1">';
      }
    } else if (heading.level < prevLevel) {
      // 레벨이 얕아질 때 UL 태그 닫기
      for (let i = prevLevel; i > heading.level; i--) {
        tocHtml += '</ul>';
      }
    }
    
    // 목차 항목 추가
    tocHtml += `<li class="my-1"><a href="#${heading.id}" class="hover:text-primary">${heading.text}</a></li>`;
    
    prevLevel = heading.level;
  });
  
  // 닫히지 않은 UL 태그 처리
  for (let i = prevLevel; i > 0; i--) {
    tocHtml += '</ul>';
  }
  
  return { tocHtml, hasToc };
}

// mermaid 다이어그램 렌더링 함수
async function renderMermaidDiagrams() {
  try {
    console.log('Mermaid 다이어그램 렌더링 시작');
    
    // mermaid 로드 확인
    if (typeof window.mermaid === 'undefined') {
      console.error('Mermaid가 로드되지 않았습니다. 잠시 후 다시 시도합니다.');
      
      // 2초 후 다시 시도
      setTimeout(() => {
        console.log('Mermaid 렌더링 재시도...');
        renderMermaidDiagrams();
      }, 2000);
      
      return;
    }
    
    console.log('Mermaid 버전:', window.mermaid?.version);
    
    // mermaid 초기화 - 밝은 색상의 테마 적용
    window.mermaid.initialize({
      startOnLoad: false,
      theme: 'neutral',  // 'default' 대신 밝은 계열의 'neutral' 테마 사용
      securityLevel: 'loose',
      fontFamily: '"Noto Sans KR", "Helvetica Neue", Arial, sans-serif',
      flowchart: { 
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis',
        defaultLinkColor: '#5C73B9', // 연결선 색상 변경 (파란 계열)
        nodeSpacing: 35,
        rankSpacing: 35
      },
      sequence: {
        diagramMarginX: 50,
        diagramMarginY: 20,
        actorMargin: 50,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35,
        mirrorActors: true,
        wrap: true
      }
    });
    
    // 다이어그램 스타일 추가
    const styleElement = document.getElementById('mermaid-style');
    if (!styleElement) {
      const style = document.createElement('style');
      style.id = 'mermaid-style';
      style.textContent = `
        .mermaid {
          background-color: #f8f9fa !important;
          border-radius: 8px;
          padding: 16px;
          margin: 16px auto !important;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          display: flex !important;
          justify-content: center !important;
          align-items: center !important;
          max-width: 100%;
        }
        .mermaid-wrapper {
          text-align: center;
          margin: 32px auto;
          width: 100%;
        }
        .mermaid svg {
          margin: 0 auto !important;
          max-width: 100%;
        }
        
        .mermaid .edgeLabel {
          color: #333;
          background-color: #f8f9fa;
          font-weight: 500;
        }
        .mermaid .node rect, 
        .mermaid .node circle, 
        .mermaid .node ellipse, 
        .mermaid .node polygon, 
        .mermaid .node path {
          fill: #EFF6FF;
          stroke: #3B82F6;
          stroke-width: 1px;
        }
        .mermaid .node .label {
          color: #1F2937;
        }
        .mermaid .cluster rect {
          fill: #F3F4F6 !important;
          stroke: #D1D5DB !important;
        }
        .mermaid .flowchart-link {
          stroke: #5C73B9 !important;
        }
      `;
      document.head.appendChild(style);
    }
    
    // mermaid 요소 찾기
    const mermaidElements = document.querySelectorAll('pre.mermaid, div.mermaid, .mermaid');
    console.log(`DOM에서 ${mermaidElements.length}개의 Mermaid 요소를 찾았습니다.`);
    
    if (mermaidElements.length === 0 && mermaidCharts.value.length > 0) {
      console.log('DOM에서 요소를 찾지 못했지만 처리된 다이어그램 정보가 있습니다. 수동으로 렌더링을 시도합니다.');
      
      // 저장된 mermaid 코드 블록으로 수동 렌더링 시도
      for (const block of mermaidCharts.value) {
        const el = document.getElementById(block.id);
        if (el) {
          console.log(`ID ${block.id}로 요소를 찾았습니다. 렌더링 시도...`);
          try {
            const { svg } = await window.mermaid.render(block.id, block.code);
            el.innerHTML = svg;
            el.classList.add('mermaid-rendered');
            console.log(`ID ${block.id} 다이어그램 렌더링 성공`);
            
            // 클릭 이벤트 제거
          } catch (err) {
            console.error(`ID ${block.id} 다이어그램 렌더링 실패:`, err);
            el.innerHTML = `
              <div class="p-4 bg-red-50 border border-red-300 rounded-md">
                <p class="text-red-500 font-medium">다이어그램 렌더링 오류</p>
                <pre class="mt-2 text-sm text-red-700 overflow-x-auto">${err.message}</pre>
                <details class="mt-2">
                  <summary class="text-sm text-gray-600 cursor-pointer">원본 코드 보기</summary>
                  <pre class="mt-1 p-2 bg-gray-100 text-xs overflow-x-auto">${block.code}</pre>
                </details>
              </div>
            `;
          }
        } else {
          console.warn(`ID ${block.id}로 요소를 찾을 수 없습니다.`);
        }
      }
      return;
    }
    
    // 모든 mermaid 요소에 대해 직접 렌더링
    if (mermaidElements.length > 0) {
      console.log('mermaid.run() 호출로 한 번에 렌더링 시도');
      try {
        window.mermaid.run({
          querySelector: '.mermaid:not(.mermaid-rendered)'
        });
        
        console.log('mermaid.run() 완료');
        
        // 각 요소에 클릭 이벤트 추가
        setTimeout(() => {
          mermaidElements.forEach(el => {
            // 이벤트 추가 제거
            if (el.getAttribute('data-click-handler')) {
              return;
            }
            
            // 클릭 이벤트를 추가하지 않음
            el.setAttribute('data-click-handler', 'true');
          });
        }, 500);
      } catch (err) {
        console.error('mermaid.run() 실패:', err);
      }
    } else {
      console.log('렌더링할 Mermaid 요소가 없습니다.');
    }
  } catch (err) {
    console.error('Mermaid 처리 오류:', err);
  }
}

// 동일 카테고리 게시물 로드
async function loadCategoryPosts() {
  if (!post.value || !post.value.category) return;
  
  try {
    // 현재 포스트의 카테고리에 속한 포스트 목록 가져오기
    const response = await api.get(`/api/posts/category/${post.value.category}`);
    
    if (response.data) {
      // 현재 포스트를 제외한 최대 5개의 동일 카테고리 포스트 표시
      categorySiblings.value = response.data
        .filter(p => p.path !== post.value.path)
        .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
        .slice(0, 5);
    }
  } catch (err) {
    console.error('동일 카테고리 포스트 로드 실패:', err);
  }
}

// 라우트 변경 감지
watch(
  () => route.fullPath,
  async () => {
    console.log('포스트 라우트 변경 감지:', route.fullPath);
    loading.value = true;
    error.value = null;
    categorySiblings.value = []; // 카테고리 게시물 목록 초기화
    previousPost.value = null; // 이전 포스트 초기화
    nextPost.value = null; // 다음 포스트 초기화
    
    try {
      const postPathParam = route.params.path;
      
      // 경로 처리: 문자열 또는 배열인 경우 모두 처리
      const postPath = Array.isArray(postPathParam) 
        ? postPathParam.join('/') 
        : postPathParam;
      
      // 포스트 경로가 없거나 undefined인 경우 처리
      if (!postPath || postPath === 'undefined') {
        throw new Error('유효하지 않은 포스트 경로입니다');
      }
      
      console.log('라우트 변경으로 로드할 포스트 경로:', postPath);
      
      // 포스트 데이터 가져오기
      const response = await api.get(`/api/posts/${postPath}`);
      
      if (!response.data) {
        throw new Error(`포스트를 찾을 수 없습니다: ${postPath}`);
      }
      
      post.value = response.data;
      
      // 마크다운을 HTML로 변환하고 mermaid 다이어그램 처리
      if (post.value && post.value.content) {
        console.log('포스트 내용 처리 시작');
        renderedContent.value = processMarkdown(post.value.content);
        
        // 동일 카테고리 게시물 로드
        await loadCategoryPosts();
        
        // 이전/다음 글 가져오기 (동일 카테고리 로드 후에 실행)
        if (post.value.category) {
          await fetchAdjacentPosts(post.value.category, post.value.path);
        }
        
        // DOM 업데이트 후 mermaid 다이어그램 렌더링
        await nextTick();
        
        // DOM 업데이트 대기를 위해 약간의 지연 추가
        setTimeout(async () => {
          console.log('DOM 업데이트 후 Mermaid 다이어그램 렌더링 시도');
          await renderMermaidDiagrams();
          
          // 목차 링크에 클릭 이벤트 추가
          setupTocLinks();
        }, 500); // 500ms 지연
      }
      
      // 카테고리 로드
      if (!postsStore.categoriesLoaded) {
        await postsStore.fetchCategories();
      }
      
    } catch (err) {
      console.error('포스트 로드 실패:', err);
      error.value = err.message || '포스트를 불러오는 중 오류가 발생했습니다.';
    } finally {
      loading.value = false;
    }
  },
  { immediate: true } // 초기 로드 시에도 실행
);

// 목차 링크 설정
function setupTocLinks() {
  const tocLinks = document.querySelectorAll('.toc-links a');
  
  tocLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);
      
      if (targetElement) {
        // 부드러운 스크롤
        targetElement.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

async function fetchAdjacentPosts(category, currentPath) {
  try {
    // 유효성 검사: 카테고리와 현재 경로가 필요함
    if (!category || !currentPath) {
      console.error('이전/다음 포스트를 가져오기 위한 카테고리 또는 경로가 없습니다');
      previousPost.value = null;
      nextPost.value = null;
      return;
    }
    
    // URL 인코딩: 특수 문자가 포함된 경로도 올바르게 처리
    const encodedCategory = encodeURIComponent(category);
    const encodedPath = encodeURIComponent(currentPath);
    
    console.log(`이전/다음 포스트 가져오기: 카테고리=${category}, 경로=${currentPath}`);
    const apiUrl = `/api/posts/${encodedCategory}/adjacent?current=${encodedPath}`;
    console.log('API 요청 URL:', apiUrl);
    
    const response = await api.get(apiUrl);
    
    if (response.data) {
      // 응답 데이터 확인 및 할당
      previousPost.value = response.data.previous || null;
      nextPost.value = response.data.next || null;
      
      // 확인 로깅
      if (previousPost.value) {
        console.log('이전 포스트 설정:', previousPost.value.title);
      } else {
        console.log('이전 포스트 없음');
      }
      
      if (nextPost.value) {
        console.log('다음 포스트 설정:', nextPost.value.title);
      } else {
        console.log('다음 포스트 없음');
      }
    }
  } catch (err) {
    console.error('이전/다음 포스트 로드 실패:', err);
    previousPost.value = null;
    nextPost.value = null;
  }
}

// 카테고리 경로 포맷
function formatCategory(categoryPath) {
  if (!categoryPath) return ''
  return categoryPath.split('/').join(' > ')
}

// 날짜 포맷
function formatDate(dateString) {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

// SEO 메타 태그 업데이트 함수
const updateMetaTags = (postData) => {
  if (!postData) return

  // 타이틀 업데이트
  document.title = `${postData.title} - 길리랩 기술 블로그`

  // 메타 태그 업데이트
  const metaTags = {
    description: postData.description || postData.title,
    'og:title': postData.title,
    'og:description': postData.description || postData.title,
    'og:type': 'article',
    'og:url': `https://gillilab.com/post/${postData.id}`,
    'og:image': postData.thumbnail_url || 'https://gillilab.com/logo.png',
    'twitter:title': postData.title,
    'twitter:description': postData.description || postData.title,
    'twitter:image': postData.thumbnail_url || 'https://gillilab.com/logo.png'
  }

  Object.entries(metaTags).forEach(([name, content]) => {
    let meta = document.querySelector(`meta[property="${name}"]`) ||
               document.querySelector(`meta[name="${name}"]`)
    
    if (!meta) {
      meta = document.createElement('meta')
      if (name.startsWith('og:')) {
        meta.setAttribute('property', name)
      } else {
        meta.setAttribute('name', name)
      }
      document.head.appendChild(meta)
    }
    meta.setAttribute('content', content)
  })

  // 구조화된 데이터 업데이트
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    'mainEntityOfPage': {
      '@type': 'WebPage',
      '@id': `https://gillilab.com/post/${postData.id}`
    },
    'headline': postData.title,
    'description': postData.description || postData.title,
    'image': postData.thumbnail_url || 'https://gillilab.com/logo.png',
    'author': {
      '@type': 'Person',
      'name': postData.author || 'Gillilab'
    },
    'publisher': {
      '@type': 'Organization',
      'name': 'Gillilab',
      'logo': {
        '@type': 'ImageObject',
        'url': 'https://gillilab.com/logo.png'
      }
    },
    'datePublished': postData.created_at,
    'dateModified': postData.updated_at || postData.created_at
  }

  let scriptTag = document.querySelector('script[type="application/ld+json"]')
  if (!scriptTag) {
    scriptTag = document.createElement('script')
    scriptTag.type = 'application/ld+json'
    document.head.appendChild(scriptTag)
  }
  scriptTag.textContent = JSON.stringify(schema)
}

// 포스트 데이터가 변경될 때마다 메타 태그 업데이트 및 애널리틱스 추적
watch(() => post.value, (newPost) => {
  if (newPost) {
    updateMetaTags(newPost)
    // 포스트 조회 추적 (Google Analytics)
    trackPostView(
      newPost.id,
      newPost.title,
      newPost.category
    )
    // 포스트 조회 추적 (네이버 서치어드바이저)
    trackNaverPostView(
      newPost.id,
      newPost.title,
      newPost.category
    )
  }
}, { immediate: true })
</script>

<style>
/* 마크다운 스타일링을 위한 추가 CSS */
.prose {
  line-height: 1.8;
  color: #374151;
  font-size: 1.05rem;
  max-width: 850px;
  margin: 0 auto;
}

.prose h1, .prose h2, .prose h3, .prose h4, .prose h5, .prose h6 {
  color: #111827;
  font-weight: 700;
  margin-top: 2.5em;
  margin-bottom: 1em;
  line-height: 1.3;
  letter-spacing: -0.01em;
}

.prose h1 { 
  font-size: 2.25em; 
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.3em;
}

.prose h2 { 
  font-size: 1.75em; 
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.3em;
}

.prose h3 { font-size: 1.5em; }
.prose h4 { font-size: 1.25em; }
.prose h5 { font-size: 1.125em; }
.prose h6 { font-size: 1em; }

.prose p {
  margin: 1.25em 0;
  line-height: 1.8;
}

.prose pre {
  background-color: #1f2937;
  color: #e5e7eb;
  padding: 1.25em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin: 1.5em 0;
  font-size: 0.9em;
  line-height: 1.6;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.prose code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.9em;
  background-color: rgba(209, 213, 219, 0.2);
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  color: #d3422e;
}

.prose pre code {
  background-color: transparent;
  padding: 0;
  color: #e5e7eb;
  border-radius: 0;
}

.prose blockquote {
  border-left: 4px solid #3b82f6;
  padding: 0.8em 1em;
  color: #4b5563;
  font-style: italic;
  margin: 1.5em 0;
  background-color: #f9fafb;
  border-radius: 0 0.3em 0.3em 0;
}

.prose a {
  color: #2563eb;
  text-decoration: none;
  border-bottom: 1px dashed #2563eb;
  transition: all 0.2s ease;
}

.prose a:hover {
  color: #1d4ed8;
  border-bottom: 1px solid #1d4ed8;
}

.prose ul, .prose ol {
  padding-left: 1.75em;
  margin: 1.25em 0;
}

.prose ul {
  list-style-type: disc;
}

.prose ol {
  list-style-type: decimal;
}

.prose li {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  line-height: 1.7;
}

.prose li > ul, .prose li > ol {
  margin: 0.5em 0;
}

.prose img {
  max-width: 100%;
  height: auto;
  border-radius: 0.5em;
  margin: 1.5em auto;
  display: block;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.prose hr {
  border: 0;
  height: 1px;
  background-color: #e5e7eb;
  margin: 2.5em 0;
}

.prose table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
  font-size: 0.95em;
  overflow: hidden;
  border-radius: 0.5em;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.prose th {
  background-color: #f3f4f6;
  font-weight: 600;
  text-align: left;
  padding: 0.85em 1em;
  border: 1px solid #d1d5db;
}

.prose td {
  padding: 0.85em 1em;
  border: 1px solid #d1d5db;
  vertical-align: top;
}

.prose tr:nth-child(even) {
  background-color: #f9fafb;
}

.prose tr:hover {
  background-color: #f3f4f6;
}

/* Mermaid 다이어그램 스타일링 */
.mermaid {
  margin: 2em auto;
  text-align: center;
  overflow-x: auto;
  background-color: #f8f9fc;
  padding: 1.5em;
  border-radius: 0.5em;
  font-family: monospace;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: center;
  width: 100%;
}

.mermaid-wrapper {
  display: flex;
  justify-content: center;
  width: 100%;
  margin: 2em auto;
}

.mermaid svg {
  max-width: 100%;
  margin: 0 auto;
}

.mermaid-rendered {
  background-color: transparent;
  padding: 0;
  box-shadow: none;
  display: flex;
  justify-content: center;
}

/* Mermaid 다이어그램의 기본 텍스트 색상 */
.mermaid .actor {
  fill: #f8fafc;
  stroke: #475569;
  stroke-width: 1px;
}

.mermaid .messageText, .mermaid .labelText, .mermaid .loopText {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  fill: #334155;
  stroke: none;
}

.mermaid .actor-line {
  stroke: #64748b;
  stroke-width: 1px;
}

.mermaid .messageLine0, .mermaid .messageLine1 {
  stroke-width: 1.5;
  stroke: #64748b;
}

.mermaid .sequenceArrow {
  fill: #64748b;
  stroke: #64748b;
}

/* Flow 다이어그램 스타일 */
.mermaid .flowchart-link {
  stroke: #64748b;
  stroke-width: 1.5;
  fill: none;
}

.mermaid .cluster rect {
  fill: #f1f5f9;
  stroke: #cbd5e1;
  stroke-width: 1px;
}

.mermaid .edgeLabel {
  background-color: #f8fafc;
  color: #334155;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 12px;
}

/* Gantt 차트 스타일 */
.mermaid .taskText {
  fill: #334155;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 12px;
}

.mermaid .taskTextOutsideRight {
  fill: #475569;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 12px;
}

.mermaid .activeTask {
  fill: #bfdbfe;
  stroke: #3b82f6;
}

/* 클래스 다이어그램 스타일 */
.mermaid .classText {
  fill: #334155;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  font-weight: bold;
}

.mermaid .node rect,
.mermaid .node circle,
.mermaid .node ellipse,
.mermaid .node polygon,
.mermaid .node path {
  fill: #f0f9ff;
  stroke: #0ea5e9;
  stroke-width: 1px;
}

/* ER 다이어그램 스타일 */
.mermaid .entityBox {
  fill: #f0f9ff;
  stroke: #0ea5e9;
}

.mermaid .attributeBoxOdd {
  fill: #f8fafc;
  stroke: #cbd5e1;
}

.mermaid .attributeBoxEven {
  fill: #f1f5f9;
  stroke: #cbd5e1;
}

/* 코드 블록 구문 강조 스타일 */
.hljs-keyword {
  color: #c678dd;
}

.hljs-string {
  color: #98c379;
}

.hljs-comment {
  color: #7f848e;
  font-style: italic;
}

.hljs-function {
  color: #61afef;
}

.hljs-number {
  color: #d19a66;
}

.hljs-operator {
  color: #56b6c2;
}

.hljs-class {
  color: #e5c07b;
}

/* 인용문 스타일 강화 */
.prose blockquote p {
  margin: 0.5em 0;
}

/* 정의 목록 스타일 */
.prose dl {
  margin: 1.25em 0;
}

.prose dt {
  font-weight: 600;
  margin-top: 1em;
}

.prose dd {
  margin-left: 1.5em;
  margin-top: 0.25em;
}

/* 각주 스타일 */
.prose .footnotes {
  font-size: 0.9em;
  color: #4b5563;
  border-top: 1px solid #e5e7eb;
  padding-top: 1em;
}

.prose .footnotes p {
  margin: 0.5em 0;
}

/* 강조 표시 */
.prose mark {
  background-color: rgba(250, 204, 21, 0.4);
  padding: 0.1em 0.2em;
  border-radius: 0.2em;
}

/* 키보드 입력 */
.prose kbd {
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 0.25em;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.1);
  padding: 0.1em 0.4em;
  font-size: 0.9em;
}

/* 목차 스타일 */
.toc-container {
  scrollbar-width: thin;
  scrollbar-color: #e5e7eb #f9fafb;
}

.toc-container::-webkit-scrollbar {
  width: 4px;
}

.toc-container::-webkit-scrollbar-track {
  background: #f9fafb;
}

.toc-container::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 6px;
}

.toc-links ul {
  border-left: 1px solid #e5e7eb;
}

.toc-links a {
  display: block;
  padding: 2px 0;
  color: #374151;
  transition: all 0.2s;
}

.toc-links a:hover {
  color: #3b82f6;
}
</style> 