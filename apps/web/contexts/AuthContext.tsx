"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { supabase } from "../lib/supabaseClient";

interface AuthUser {
  id: string;
  email: string;
  role: string;
  permissions: string[];
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  isLoading: boolean;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  isAdmin: boolean;
  isDeliveryPerson: boolean;
  isCustomer: boolean;
}

// Role-based permission mapping (fallback if DB query fails)
const ROLE_PERMISSIONS: Record<string, string[]> = {
  admin: [
    "view_tracking",
    "access_knowledge_base",
    "perform_analysis",
    "access_chat",
    "full_admin_access",
  ],
  delivery_person: [
    "view_tracking",
    "report_incident",
    "access_chat",
  ],
  customer: [
    "place_order",
    "view_tracking",
    "access_chat",
  ],
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch user role and permissions from database
  const fetchUserRoleAndPermissions = async (userId: string, userEmail: string) => {
    try {
      // Get user's role
      const { data: userRoles, error: roleError } = await supabase
        .from('user_roles')
        .select(`
          roles (
            role_name,
            role_permissions (
              permissions (
                permission_name
              )
            )
          )
        `)
        .eq('user_id', userId)
        .single();

      if (roleError || !userRoles) {
        console.error('Error fetching user role:', roleError);
        // Default to customer role if no role found
        return {
          role: 'customer',
          permissions: ROLE_PERMISSIONS.customer
        };
      }

      const role = (userRoles as any).roles.role_name;
      const permissions = (userRoles as any).roles.role_permissions.map(
        (rp: any) => rp.permissions.permission_name
      );

      return { role, permissions };
    } catch (error) {
      console.error('Error in fetchUserRoleAndPermissions:', error);
      return {
        role: 'customer',
        permissions: ROLE_PERMISSIONS.customer
      };
    }
  };

  useEffect(() => {
    // Check for existing Supabase session
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session?.user) {
        const { role, permissions } = await fetchUserRoleAndPermissions(
          session.user.id,
          session.user.email || ''
        );
        
        setUser({
          id: session.user.id,
          email: session.user.email || '',
          role,
          permissions
        });
        setToken(session.access_token);
      }
      
      setIsLoading(false);
    };

    checkSession();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        const { role, permissions } = await fetchUserRoleAndPermissions(
          session.user.id,
          session.user.email || ''
        );
        
        setUser({
          id: session.user.id,
          email: session.user.email || '',
          role,
          permissions
        });
        setToken(session.access_token);
      } else {
        setUser(null);
        setToken(null);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const login = async (newToken: string) => {
    try {
      // Get the current session from Supabase
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session?.user) {
        const { role, permissions } = await fetchUserRoleAndPermissions(
          session.user.id,
          session.user.email || ''
        );
        
        setUser({
          id: session.user.id,
          email: session.user.email || '',
          role,
          permissions
        });
        setToken(newToken);
      }
    } catch (error) {
      console.error("Failed to process login:", error);
    }
  };

  const logout = async () => {
    await supabase.auth.signOut();
    localStorage.removeItem("authToken");
    setUser(null);
    setToken(null);
  };

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    return user.permissions.includes(permission);
  };

  const hasRole = (role: string): boolean => {
    if (!user) return false;
    return user.role === role;
  };

  const isAdmin = user?.role === "admin";
  const isDeliveryPerson = user?.role === "delivery_person";
  const isCustomer = user?.role === "customer";

  const value = { 
    user, 
    token, 
    login, 
    logout, 
    isLoading,
    hasPermission,
    hasRole,
    isAdmin,
    isDeliveryPerson,
    isCustomer,
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        Loading Application...
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
