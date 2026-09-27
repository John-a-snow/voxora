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


                <div className="relative h-[400px] md:h-[600px] w-full hidden md:block">

                    <div className="absolute top-0 right-10 w-64 bg-brand-panel p-3 pb-12 brutal-border brutal -shadow rotate-6 z-10 transition-transform hover:scale-105 hover:rotate-12 hover:z-30">
                        <div className="bg-brand-inverted w-full h-40 flex items-center justify-center p-4">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-brand-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLineJoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                            </svg>
                        </div>
                        <div className="absolute bottom-4 left-0 w-full text-center">
                            <span className="bg-brand-inverted text-brand-inverted-text px-3 py-1 font-mono text-xs font-bold uppercase tracking-widest">
                                Audio Processing
                            </span>
                        </div>
                    </div>


                    <div className="absolute top-32 left-10 w-72 bg-brand-panel p-3 pb-12 brutal-border brutal-shadow -rotate-6 z-20 transition-transform hover:scale-105 hover:-rotate-12 hover:z-30">
                        <div className="bg-yellow-300 w-full h-48 flex items-center justify-center p-4 border-2 border-brand-border">
                            <svg xmlns="https://www.w3.org/2000/svg"className="h-20 w-20 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                              </svg>
                        </div>
                        <div className="absolute bottom-4 left-0 w-full text-center">
                            <span className="bg-brand-inverted text-brand-inverted-text px-3 py-1 font-mono text-xs font-bold uppercase tracking-widest">
                                Vector Retrieval
                            </span>
                        </div>
                    </div>


                    <div className="absolute bottom-10 right-20 w-64 bg-brand-panel p-3 pb-12 brutal-border brutal-shadow rotate-3 z-10 transition-transform hover:scale-105 hover:rotate-6 hover:z-30">
                        <div className="bg-blue-100 w-full h-36 flex items-center justify-center p-4 border-2 border-brand-border">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                        </div>
                        <div className="absolute bottom-4 left-0 w-full text-center">
                            <span className="bg-brand-inverted text-brand-inverted-text px-3 py-1 font-mono text-xs font-bold uppercase tracking-widest">
                                Grounding Check
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    )
};

