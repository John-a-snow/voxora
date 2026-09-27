export const Hero = () => {
    return (
        <header className="mb-16">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">


                <div className="flex flex-col gap-8 relative z-10">
                    <div className="inline-flex items-center gap-3 bg-brand-panel brutal-border brutal-shadow px-4 py-2 self-start">
                        <div className="w-6 h-6 bg-brand-primary flex items-center justify-center rounded-sm">
                            <svg xmlns="https://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                            </svg>
                        </div>
                        <span className="font-mono font-bold text-sm tracking-widest uppercase text-brand-text">
                            Generative AI Agent
                        </span>
                    </div>

                    <div>
                        <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tighter leading-[0.9] text-brand-text">
                         Voxora <br/>
                         <span className="text-brand-primary">Knowledge </span>
                        </h1>
                    </div>

                    <p className="text-xl md:text-2xl font-medium text-brand-text leading-relaxed max-w-xl">
                        The official voice-activated knowledge retrieval system - speak naturally, retrieve evidence, and ground every answer. 
                    </p>

                    <div className="flex flex-wrap items-center gap-4 mt-2">
                        <button className="bg-brand-primary text-white brutal-border brutal-shadow brutal-shadow-hover px-8 py-4 font-black uppercase tracking-widest flex items-center gap-3">
                            Start Query 
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                        </button>
                        <button className="bg-brand-panel text-brand-text brutal-border brutal-shadow brutal-shadow-hover px-8 py-4 font-black uppercase tracking-widest">
                            Explore Logs
                        </button>
                    </div>
                </div>

            <div className="max-w-4xl">
                <h1 className="text-6xl md:text-8xl font-black tracking-tighter uppercase leading-none mb-6">
                    Ask The<br />Voxora.
                </h1>
                <p className="text-lg md:text-xl font-medium max-w-2xl text-gray-800 leading-relaxed border-l-4 border-brand-primary pl-4">
                    Speak a question. Retrieve evidence. Get an answer grounded in the provided knowledge base.
                </p>
            </div>
        </header>
    )
};

