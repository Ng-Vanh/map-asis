import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Message from './Message';
import MessageInput from './MessageInput';

// Helper functions to format different types of responses
const formatPlacesList = (places, intent, summary = '') => {
  if (!places || places.length === 0) {
    return 'Không tìm thấy địa điểm nào phù hợp.';
  }
  
  let result = '';
  
  // Display summary first if available
  if (summary) {
    result += `${summary}\n\n---\n\n`;
  }
  
  result += `### Tìm thấy ${places.length} địa điểm:\n\n`;
  
  places.forEach((place, index) => {
    // Display name (with English translation if available)
    if (place.name_en && place.name_en !== place.name) {
      result += `**${index + 1}. ${place.name}** (${place.name_en})\n\n`;
    } else {
      result += `**${index + 1}. ${place.name}**\n\n`;
    }
    
    // Display images first (max 2)
    if (place.images && place.images.length > 0) {
      const imagesToShow = place.images.slice(0, 2);
      imagesToShow.forEach(imgUrl => {
        result += `![${place.name}](${imgUrl})\n\n`;
      });
    }
    
    // Basic info
    if (place.address) result += `📍 **Địa chỉ:** ${place.address}\n\n`;
    if (place.categories && place.categories.length > 0) {
      result += `🏷️ **Loại:** ${place.categories.join(', ')}\n\n`;
    }
    if (place.distance_meters !== undefined) {
      result += `📏 **Khoảng cách:** ${place.distance_meters}m\n\n`;
    }
    
    // Phase 1: Opening hours
    if (place.is_open_now !== undefined) {
      const status = place.is_open_now ? '🟢 Đang mở cửa' : '🔴 Đã đóng cửa';
      result += `⏰ **Trạng thái:** ${status}\n\n`;
    }
    
    // Phase 1: Price info
    if (place.estimated_cost || place.price_info) {
      const priceInfo = place.estimated_cost || place.price_info;
      if (priceInfo.price_range) {
        result += `💰 **Giá:** ${priceInfo.price_range} `;
      }
      if (priceInfo.per_person || priceInfo.min_price) {
        const min = priceInfo.per_person?.min || priceInfo.min_price;
        const max = priceInfo.per_person?.max || priceInfo.max_price;
        result += `(${min?.toLocaleString()} - ${max?.toLocaleString()} VND)\n\n`;
      } else {
        result += '\n\n';
      }
    }
    
    // Phase 1: Contact info
    if (place.contact_info) {
      if (place.contact_info.phone) {
        result += `📞 **Phone:** ${place.contact_info.phone}\n\n`;
      }
      if (place.contact_info.website) {
        result += `🌐 **Website:** [${place.contact_info.website}](${place.contact_info.website})\n\n`;
      }
    }
    
    // Phase 1: Google Maps link
    if (place.google_maps_url) {
      result += `🗺️ **[Xem trên Google Maps](${place.google_maps_url})**\n\n`;
    }
    
    // Phase 1: Directions
    if (place.directions) {
      result += `🚶 **Chỉ đường:** ${place.directions.distance?.meters}m (~${place.directions.estimated_time?.minutes} phút)\n\n`;
      if (place.suggested_transport) {
        const transportIcons = {
          walking: '🚶',
          bicycling: '🚴',
          driving: '🚗',
          transit: '🚌'
        };
        result += `${transportIcons[place.suggested_transport] || '🚗'} **Đề xuất:** ${place.suggested_transport}\n\n`;
      }
      if (place.directions.directions_url) {
        result += `📍 **[Chỉ đường chi tiết](${place.directions.directions_url})**\n\n`;
      }
    }
    
    // Summary
    if (place.summary) {
      result += `💡 ${place.summary}\n\n`;
    }
    
    result += '---\n\n';
  });
  
  return result;
};

const formatRecommendations = (recommendations) => {
  if (!recommendations || recommendations.length === 0) {
    return 'Không có gợi ý nào phù hợp.';
  }
  
  let result = '### 🎯 Gợi ý địa điểm cho bạn:\n\n';
  recommendations.forEach((place, index) => {
    result += `**${index + 1}. ${place.name}**\n`;
    if (place.address) result += `📍 ${place.address}\n`;
    if (place.match_reason) result += `💡 ${place.match_reason}\n`;
    if (place.score !== undefined) result += `⭐ Score: ${place.score.toFixed(2)}\n`;
    result += '\n';
  });
  
  return result;
};

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Xin chào! Tôi là trợ lý du lịch AI của bạn. 🌟\n\n**✨ Phase 1 Features:**\n- 🌐 **Đa ngôn ngữ** - Hỗ trợ Tiếng Việt & English\n- 🗺️ **Maps & Chỉ đường** - Google Maps tích hợp\n- ⏰ **Giờ mở cửa** - Kiểm tra trạng thái real-time\n- 💰 **Ước tính chi phí** - Lọc theo ngân sách\n\n**Tôi có thể giúp bạn:**\n- 🔍 Tìm kiếm địa điểm (với giá, giờ mở cửa)\n- 📍 Tìm địa điểm gần đây (có chỉ đường)\n- 🎯 Gợi ý địa điểm (theo ngân sách)\n- 📊 So sánh địa điểm (so sánh giá)\n- 🗺️ Lên lịch trình (với tổng chi phí)\n- 💡 Chat tự nhiên bằng Tiếng Việt hoặc English\n\n**Ví dụ:**\n- "Tìm quán cafe gần Hồ Gươm"\n- "Find restaurants near Hoan Kiem Lake" (English)\n- "Lập lịch trình 1 ngày Old Quarter với ngân sách 500k"\n- "So sánh giá giữa các nhà hàng"\n\nBạn muốn khám phá điều gì ở Hà Nội? 🏮',
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (userMessage) => {
    // Add user message
    const newUserMessage = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8864/api/v1/chat', {
        message: userMessage
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      // Format response content based on API structure
      let content = '';
      const data = response.data;
      
      if (data.success && data.result) {
        // Handle different intent types
        if (data.result.itinerary) {
          // Plan itinerary intent
          content = data.result.itinerary;
        } else if (data.result.response) {
          // General response
          content = data.result.response;
        } else if (data.result.comparison) {
          // Compare places intent
          content = data.result.comparison;
        } else if (data.result.nearby_places) {
          // Nearby landmark - has summary and nearby_places
          content = formatPlacesList(
            data.result.nearby_places, 
            data.intent, 
            data.result.summary
          );
        } else if (data.result.places) {
          // Search/semantic places
          content = formatPlacesList(
            data.result.places, 
            data.intent,
            data.result.recommendation || data.result.summary
          );
        } else if (data.result.recommendations) {
          // Recommend places
          content = formatRecommendations(data.result.recommendations);
        } else {
          // Fallback - try to display result as JSON
          content = JSON.stringify(data.result, null, 2);
        }
      } else if (data.response) {
        // Direct response field
        content = data.response;
      } else {
        content = 'Xin lỗi, tôi không thể xử lý yêu cầu này.';
      }

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: content,
        intent: data.intent,
        confidence: data.confidence,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `❌ Lỗi kết nối: ${error.message}\n\nVui lòng kiểm tra:\n- Server đang chạy ở http://localhost:8864\n- Các service (Neo4j, Qdrant, Embedding) đang hoạt động`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col" style={{ height: '70vh' }}>
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map(message => (
          <Message key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-6 py-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <MessageInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatInterface;
