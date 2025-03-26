// Google Analytics 이벤트 추적
export const trackEvent = (category, action, label = null, value = null) => {
  if (window.gtag) {
    gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value
    });
  }
};

// 페이지 조회 추적
export const trackPageView = (path, title = null) => {
  if (window.gtag) {
    gtag('event', 'page_view', {
      page_path: path,
      page_title: title || document.title
    });
  }
};

// 게시물 조회 추적
export const trackPostView = (postId, postTitle, category) => {
  if (window.gtag) {
    gtag('event', 'view_item', {
      items: [{
        id: postId,
        title: postTitle,
        category: category
      }]
    });
  }
};

// 검색 이벤트 추적
export const trackSearch = (searchTerm) => {
  if (window.gtag) {
    gtag('event', 'search', {
      search_term: searchTerm
    });
  }
};

// 카테고리 조회 추적
export const trackCategoryView = (category) => {
  if (window.gtag) {
    gtag('event', 'view_category', {
      category: category
    });
  }
}; 