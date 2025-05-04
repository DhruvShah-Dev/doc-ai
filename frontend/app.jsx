const { useState, useRef, useEffect } = React;

const backendUrl = "http://localhost:8000"; // Backend server

function App() {
    const [messages, setMessages] = useState([
        {
            id: 1,
            text: "Hello! I'm Binghamton University's Document Chatbot. Upload your documents and ask me questions about them!",
            sender: 'bot'
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [documents, setDocuments] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isDragActive, setIsDragActive] = useState(false);
    const fileInputRef = useRef(null);
    const messagesEndRef = useRef(null);

    const handleSendMessage = async () => {
        if (inputValue.trim() === '') return;
    
        const newUserMessage = {
            id: messages.length + 1,
            text: inputValue,
            sender: 'user'
        };
    
        setMessages(prev => [...prev, newUserMessage]);
        setInputValue('');
        setIsLoading(true);
    
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
    
            const response = await fetch(`${backendUrl}/ask/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'  // Explicitly expect JSON
                },
                body: new URLSearchParams({ question: inputValue }),
                signal: controller.signal
            });
    
            clearTimeout(timeoutId);
    
            // First check if response is OK
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Failed to get AI response');
            }
    
            // Then try to parse JSON
            const data = await response.json();
            
            if (!data.answer) {
                throw new Error('Invalid response format from server');
            }
    
            const newBotMessage = {
                id: messages.length + 2,
                text: data.answer,
                sender: 'bot'
            };
            setMessages(prev => [...prev, newBotMessage]);
        } catch (err) {
            console.error('Error details:', err);
            const newBotMessage = {
                id: messages.length + 2,
                text: `Error: ${err.message}`,
                sender: 'bot'
            };
            setMessages(prev => [...prev, newBotMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    const handleFileChange = async (e) => {
        const files = Array.from(e.target.files);
        if (!files.length) return;
    
        const formData = new FormData();
        formData.append('file', files[0]);
    
        try {
            setIsLoading(true);
            const res = await fetch(`${backendUrl}/upload/`, {
                method: 'POST',
                body: formData
            });
    
            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.error || 'Upload failed');
            }
    
            const data = await res.json();
            console.log('Upload success:', data);
    
            const newDoc = {
                id: Date.now() + Math.random(),
                name: files[0].name,
                type: files[0].type,
                size: files[0].size,
                lastModified: files[0].lastModified
            };
            setDocuments(prev => [...prev, newDoc]);
    
            const newBotMessage = {
                id: messages.length + 1,
                text: `I've received "${files[0].name}". You can now ask me questions about it.`,
                sender: 'bot'
            };
            setMessages(prev => [...prev, newBotMessage]);
        } catch (err) {
            console.error('Upload error:', err);
            const newBotMessage = {
                id: messages.length + 1,
                text: `Error processing "${files[0].name}": ${err.message}`,
                sender: 'bot'
            };
            setMessages(prev => [...prev, newBotMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') setIsDragActive(true);
        else if (e.type === 'dragleave') setIsDragActive(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const files = Array.from(e.dataTransfer.files);
            files.forEach(file => handleFileChange({ target: { files: [file] } }));
        }
    };

    const triggerFileInput = () => {
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
            fileInputRef.current.click();
        }
    };

    const removeDocument = (id) => {
        setDocuments(prev => prev.filter(doc => doc.id !== id));
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header className="bg-bu-green text-white shadow-md">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <img src="https://www.binghamton.edu/images/bu-logo.svg" alt="BU Logo" className="h-12" />
                        <div>
                            <h1 className="text-xl font-bold">Binghamton University</h1>
                            <p className="text-sm opacity-80">Document-Based Chatbot</p>
                        </div>
                    </div>
                    <div className="hidden md:flex items-center space-x-2">
                        <span className="px-3 py-1 bg-white bg-opacity-20 rounded-full text-sm">Research Assistant</span>
                    </div>
                </div>
            </header>

            {/* Main */}
            <main className="flex-1 container mx-auto px-4 py-6 flex flex-col md:flex-row gap-6">
                {/* Left Panel */}
                <div className="w-full md:w-1/3 lg:w-1/4 bg-white rounded-lg shadow-md p-4 flex flex-col">
                    <h2 className="text-lg font-semibold text-bu-green mb-4 flex items-center">
                        <i className="fas fa-file-alt mr-2"></i> Your Documents
                    </h2>

                    {/* Dropzone */}
                    <div
                        className={`file-dropzone flex-1 flex flex-col items-center justify-center p-6 mb-4 rounded-lg cursor-pointer ${isDragActive ? 'active' : ''}`}
                        onDragEnter={handleDrag}
                        onDragOver={handleDrag}
                        onDragLeave={handleDrag}
                        onDrop={handleDrop}
                        onClick={triggerFileInput}
                    >
                        <i className="fas fa-cloud-upload-alt text-3xl text-gray-400 mb-2"></i>
                        <p className="text-center text-gray-600">Drag & drop or click to upload</p>
                        <p className="text-xs text-gray-500 mt-2">Supported: PDF, DOCX, TXT, PPTX</p>
                        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" multiple />
                    </div>

                    {/* Uploaded Documents */}
                    <div className="flex-1 overflow-y-auto">
                        {documents.length === 0 ? (
                            <div className="text-center text-gray-500 py-4">
                                <i className="fas fa-folder-open text-2xl mb-2"></i>
                                <p>No documents uploaded yet</p>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                {documents.map(doc => (
                                    <div key={doc.id} className="document-card bg-white border border-gray-200 rounded-lg p-3 flex items-start justify-between transition-all duration-200">
                                        <div className="flex items-start space-x-2">
                                            <i className="fas fa-file-alt text-gray-500 mt-1"></i>
                                            <div>
                                                <p className="text-sm font-medium text-gray-800 truncate max-w-xs">{doc.name}</p>
                                                <p className="text-xs text-gray-500">{Math.round(doc.size / 1024)} KB • {new Date(doc.lastModified).toLocaleDateString()}</p>
                                            </div>
                                        </div>
                                        <button onClick={() => removeDocument(doc.id)} className="text-gray-400 hover:text-red-500">
                                            <i className="fas fa-times"></i>
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Add More Button */}
                    <div className="mt-4 pt-4 border-t border-gray-200">
                        <button
                            className="w-full bg-bu-green hover:bg-green-800 text-white py-2 px-4 rounded-lg flex items-center justify-center"
                            onClick={triggerFileInput}
                        >
                            <i className="fas fa-plus mr-2"></i> Add More Documents
                        </button>
                    </div>
                </div>

                {/* Chat Panel */}
                <div className="flex-1 flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
                    {/* Chat Header */}
                    <div className="bg-bu-green text-white px-4 py-3 flex items-center">
                        <div className="w-8 h-8 rounded-full bg-white bg-opacity-20 flex items-center justify-center mr-3">
                            <i className="fas fa-robot"></i>
                        </div>
                        <div>
                            <h3 className="font-semibold">BU Document Assistant</h3>
                            <p className="text-xs opacity-80">{documents.length > 0 ? `Ready to answer questions about ${documents.length} document(s)` : 'Upload documents to get started'}</p>
                        </div>
                    </div>

                    {/* Chat Messages */}
                    <div className="flex-1 p-4 overflow-y-auto space-y-4">
                        {messages.map(message => (
                            <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-3xl px-4 py-3 ${message.sender === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot'}`}>
                                    <p className="text-gray-800">{message.text}</p>
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="chat-bubble-bot px-4 py-3 max-w-3xl">
                                    <div className="flex space-x-2 items-center">
                                        <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                                        <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                        <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Chat Input */}
                    <div className="border-t border-gray-200 p-4 bg-gray-50">
                        <div className="flex items-center space-x-2">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask a question about your documents..."
                                className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-bu-green focus:border-transparent"
                            />
                            <button
                                onClick={handleSendMessage}
                                disabled={inputValue.trim() === ''}
                                className={`w-10 h-10 rounded-full flex items-center justify-center ${inputValue.trim() === '' ? 'bg-gray-200 text-gray-500' : 'bg-bu-green text-white hover:bg-green-800'}`}
                            >
                                <i className="fas fa-paper-plane"></i>
                            </button>
                        </div>
                        <p className="text-xs text-gray-500 mt-2 text-center">BU AI Assistant may generate inaccurate answers.</p>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="bg-bu-green text-white py-6">
                <div className="container mx-auto px-4">
                    <p className="text-center text-xs">© {new Date().getFullYear()} Binghamton University</p>
                </div>
            </footer>
        </div>
    );
}
