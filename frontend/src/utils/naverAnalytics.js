import { config } from '../config'

// 네이버 서치어드바이저 이벤트 추적
export const trackNaverEvent = (eventName, eventData = {}) => {
  if (window.wcs) {
    window.wcs.add({
      wa: config.naverSiteId,
      event: eventName,
      ...eventData
    });
  }
};

// 페이지 조회 추적
export const trackNaverPageView = (path, title = null) => {
  if (window.wcs) {
    window.wcs.add({
      wa: config.naverSiteId,
      event: 'page_view',
      path: path,
      title: title || document.title
    });
  }
};

// 게시물 조회 추적
export const trackNaverPostView = (postId, postTitle, category) => {
  if (window.wcs) {
    window.wcs.add({
      wa: config.naverSiteId,
      event: 'post_view',
      post_id: postId,
      post_title: postTitle,
      category: category
    });
  }
};

// 검색 이벤트 추적
export const trackNaverSearch = (searchTerm) => {
  if (window.wcs) {
    window.wcs.add({
      wa: config.naverSiteId,
      event: 'search',
      search_term: searchTerm
    });
  }
};

// 카테고리 조회 추적
export const trackNaverCategoryView = (category) => {
  if (window.wcs) {
    window.wcs.add({
      wa: config.naverSiteId,
      event: 'category_view',
      category: category
    });
  }
}; 